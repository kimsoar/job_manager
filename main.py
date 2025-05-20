import click
import asyncio
from manager.job_registry import get_all_jobs, get_job_by_name
from manager.job_executor import JobExecutor
from utils.db import db_instance
import jobs  # register all jobs

@click.group()
def cli():
    """Job Manager CLI"""
    pass

@cli.command()
@click.option('--only', multiple=True, help="Run only specific job(s) by name")
def run(only):
    """Run jobs (all or selected)"""
    async def main():
        await db_instance.connect()

        if only:
            selected = get_job_by_name(only)
            if not selected:
                click.echo("No jobs found.")
                return
        else:
            selected = get_all_jobs()

        executor = JobExecutor(selected)
        try:
            await executor.run_all()
        except KeyboardInterrupt:
            click.echo("Received Ctrl+C. Cancelling tasks...")

    asyncio.run(main())

@cli.command()
def list():
    """List all available jobs"""
    for name, _ in get_all_jobs():
        click.echo(f"- {name}")

if __name__ == "__main__":
    cli()
