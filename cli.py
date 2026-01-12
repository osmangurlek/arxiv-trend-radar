"""
ArXiv Trend Radar - CLI Tool
Usage:
    python cli.py ingest --query "retrieval augmented generation" --days 7 --limit 50
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

load_dotenv()


async def ingest_command_async(args):
    """Ingest papers from arXiv API with entity extraction"""
    db = SessionLocal()
    try:
        # Initialize repositories
        paper_repo = PaperRepository(db)
        entity_repo = EntityRepository(db)
        
        # Initialize LLM service
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY not found in environment variables.")
            print("   Please add it to your .env file.")
            return
        
        llm_service = LLMService(api_key=api_key)
        
        # Initialize ingestion service with all dependencies
        service = IngestionService(
            paper_repo=paper_repo,
            entity_repo=entity_repo,
            llm_service=llm_service
        )
        
        print(f"\n📥 Ingesting papers...")
        print(f"   Query: {args.query}")
        print(f"   Days: {args.days}")
        print(f"   Limit: {args.limit}")
        print("-" * 50)
        
        count = await service.fetch_and_save(query=args.query, max_results=args.limit)
        
        db.commit()  # Commit all changes
        
        print("-" * 50)
        print(f"✅ Successfully ingested {count} papers with entity extraction.\n")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def ingest_command(args):
    """Wrapper to run async ingest command"""
    asyncio.run(ingest_command_async(args))


def digest_command(args):
    """Generate weekly digest (not yet implemented)"""
    print(f"\n📝 Generating digest for week starting: {args.week_start}")
    print("⚠️  Digest generation not yet implemented.\n")


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
    elif args.command == "digest":
        digest_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
