"""
ArXiv Trend Radar - CLI Tool
Usage:
    python cli.py ingest --query "retrieval augmented generation" --days 7 --limit 50
    python cli.py canonicalize
    python cli.py digest --week-start 2026-01-01
"""
import argparse
import asyncio
import os
from dotenv import load_dotenv

from backend.app.database import SessionLocal
from backend.app.repositories.paper_repo import PaperRepository
from backend.app.repositories.entity_repo import EntityRepository
from backend.app.services.ingestion_services import IngestionService
from backend.app.llm.entity_extraction import LLMService
from backend.app.llm.paper_classification import ClassificationService
from backend.app.llm.canonicalization import CanonicalizationService

load_dotenv()


async def ingest_command_async(args):
    """Ingest papers from arXiv API with entity extraction"""
    db = SessionLocal()
    try:
        # Initialize repositories
        paper_repo = PaperRepository(db)
        entity_repo = EntityRepository(db)
        
        # Initialize LLM service
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Error: OPENAI_API_KEY not found in environment variables.")
            print("   Please add it to your .env file (use your OpenRouter API key).")
            return
        
        llm_service = LLMService(api_key=api_key)
        classification_service = ClassificationService(api_key=api_key)
        
        # Initialize ingestion service with all dependencies
        service = IngestionService(
            paper_repo=paper_repo,
            entity_repo=entity_repo,
            llm_service=llm_service,
            classification_service=classification_service
        )
        
        print(f"\n📥 Ingesting papers...")
        print(f"   Query: {args.query}")
        print(f"   Days: {args.days}")
        print(f"   Limit: {args.limit}")
        print("-" * 50)
        
        count, saved_papers = await service.fetch_and_save(query=args.query, max_results=args.limit)
        
        db.commit()  # Commit all changes
        
        print("-" * 50)
        print(f"✅ Successfully ingested {count} papers with entity extraction.\n")
        from collections import defaultdict
        by_day = defaultdict(list)
        for p in saved_papers:
            day = (p["published_at"][:10] if isinstance(p["published_at"], str) else str(p["published_at"])[:10])
            by_day[day].append(p)
        for day in sorted(by_day.keys(), reverse=True):
            print(f"📅 {day}")
            for p in by_day[day]:
                title_short = (p["title"][:72] + "…") if len(p["title"]) > 72 else p["title"]
                print(f"   • {p['arxiv_id']}  {title_short}")
            print()
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def ingest_command(args):
    """Wrapper to run async ingest command"""
    asyncio.run(ingest_command_async(args))


async def canonicalize_command_async():
    """Find and merge duplicate entities"""
    db = SessionLocal()
    try:
        entity_repo = EntityRepository(db)
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Error: OPENAI_API_KEY not found.")
            return

        # Get all entities without canonical_id
        entities = entity_repo.get_entities_without_canonical()
        if not entities:
            print("⚠️  No entities to canonicalize.")
            return
        
        entity_names = [e.name for e in entities]
        print(f"\n🔍 Analyzing {len(entity_names)} entities for duplicates...")
        
        # Call LLM to find canonical groups
        service = CanonicalizationService(api_key=api_key)
        result = await service.find_canonical_groups(entity_names)
        
        if not result.groups:
            print("✅ No duplicates found.")
            return
        
        # Apply canonical mappings
        for group in result.groups:
            print(f"\n📌 Canonical: {group.canonical}")
            print(f"   Aliases: {group.aliases}")
            
            # Find or get canonical entity
            canonical_entity = entity_repo.get_entity_by_name(group.canonical)
            if not canonical_entity:
                # If canonical doesn't exist, use first alias as canonical
                canonical_entity = entity_repo.get_entity_by_name(group.aliases[0]) if group.aliases else None
            
            if canonical_entity:
                for alias_name in group.aliases:
                    alias_entity = entity_repo.get_entity_by_name(alias_name)
                    if alias_entity and alias_entity.id != canonical_entity.id:
                        entity_repo.set_canonical_id(alias_entity.id, canonical_entity.id)
                        print(f"   ✅ Linked: {alias_name} → {canonical_entity.name}")
        
        db.commit()
        print(f"\n✅ Canonicalization complete!\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def canonicalize_command(args):
    """Wrapper to run async canonicalize command"""
    asyncio.run(canonicalize_command_async())


async def digest_command_async(args):
    """Generate weekly digest from database facts"""
    from datetime import datetime, timedelta
    from backend.app.llm.digest_generator import DigestService
    from backend.app.repositories import analytics_repo
    from backend.app.models.models import Digest
    
    db = SessionLocal()
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Error: OPENAI_API_KEY not found.")
            return

        # Parse week_start date
        week_start = datetime.strptime(args.week_start, "%Y-%m-%d")
        week_end = week_start + timedelta(days=7)
        
        print(f"\n📝 Generating digest for week: {args.week_start}")
        print("-" * 50)
        
        # Gather analytics data from DB
        print("📊 Fetching analytics data...")
        top_entities = analytics_repo.get_top_entities_by_week(db, week_start, "method", limit=10)
        fastest_growing = analytics_repo.get_fastest_growing_entities(db, "method")
        cooccurrence = analytics_repo.get_entity_cooccurence_edges(db, "method", days=7)
        categories = analytics_repo.category_distribution_over_time(db)
        
        # Format for LLM
        top_list = [{"name": r[0], "count": r[1]} for r in top_entities]
        growth_list = [{"name": r[0], "growth": r[1]} for r in fastest_growing]
        cooc_list = [{"entity_a": r[0], "entity_b": r[1], "count": r[2]} for r in cooccurrence[:10]]
        cat_list = [{"category": r[1], "count": r[2]} for r in categories[:10]]
        
        print(f"   Top entities: {len(top_list)}")
        print(f"   Growing entities: {len(growth_list)}")
        print(f"   Co-occurrences: {len(cooc_list)}")
        
        # Generate digest with LLM
        print("\n🤖 Generating digest with LLM...")
        service = DigestService(api_key=api_key)
        content = await service.generate_digest(
            week_start=week_start.date(),
            top_entities=top_list,
            fastest_growing=growth_list,
            cooccurrence=cooc_list,
            categories=cat_list
        )
        
        # Save to database
        digest = Digest(
            week_start=week_start,
            week_end=week_end,
            content_md=content
        )
        db.add(digest)
        db.commit()
        
        print("-" * 50)
        print("\n📄 Generated Digest:\n")
        print(content)
        print("\n" + "=" * 50)
        print("✅ Digest saved to database!\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def digest_command(args):
    """Wrapper to run async digest command"""
    asyncio.run(digest_command_async(args))


def main():
    parser = argparse.ArgumentParser(
        description="ArXiv Trend Radar CLI",
        prog="cli.py"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest papers from arXiv")
    ingest_parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="Search query for arXiv"
    )
    ingest_parser.add_argument(
        "--days", "-d",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    ingest_parser.add_argument(
        "--limit", "-l",
        type=int,
        default=50,
        help="Maximum number of papers to fetch (default: 50)"
    )
    
    # Canonicalize command
    subparsers.add_parser("canonicalize", help="Find and merge duplicate entities")
    
    # Digest command
    digest_parser = subparsers.add_parser("digest", help="Generate weekly digest")
    digest_parser.add_argument(
        "--week-start", "-w",
        type=str,
        required=True,
        help="Start date of the week (YYYY-MM-DD)"
    )
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest_command(args)
    elif args.command == "canonicalize":
        canonicalize_command(args)
    elif args.command == "digest":
        digest_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
