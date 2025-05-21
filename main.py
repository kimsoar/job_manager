import click
import asyncio
from manager.job_registry import get_all_jobs, get_job_by_name
from manager.job_executor import JobExecutor
from utils.db import db_instance
import jobs  # register all jobs


RUN_HELP_MESSAGE = """
⚠️ Usage instructions:
    Run all jobs: python main.py run --all
    Run specific jobs: python main.py run --only job_name [--only job_name2 ...]
    View the list of registered jobs: python main.py list
"""


@click.group()
def cli():
    """Job Manager CLI"""
    pass


@cli.command()
@click.option('--only', multiple=True, help="Run only specific job(s) by name")
@click.option('--all', 'run_all', is_flag=True, help="Run all registered jobs")
def run(only, run_all):
    """Run jobs (all or selected)"""
    async def main():
        await db_instance.connect()

        if only:
            selected = get_job_by_name(only)
            if not selected:
                click.echo("❌ No matching jobs found.")
                return
        elif run_all:
            selected = get_all_jobs()
        else:
            click.echo(RUN_HELP_MESSAGE)
            return

        executor = JobExecutor(selected)
        try:
            await executor.run_all()
        except KeyboardInterrupt:
            click.echo("Received Ctrl+C. Cancelling tasks...")

    asyncio.run(main())

@cli.command()
def list():
    """List all available jobs"""
    click.echo("📋 Registered Job List:")
    for name, _ in get_all_jobs():
        click.echo(f"- {name}")

if __name__ == "__main__":
    cli()
