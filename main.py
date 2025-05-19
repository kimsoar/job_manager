import click
import asyncio
from manager.job_registry import get_all_jobs, get_job_by_name
from manager.job_executor import JobExecutor
import jobs  # trigger registration

@click.group()
def cli():
    """Job Manager CLI"""
    pass

@cli.command()
@click.option('--only', multiple=True, help="Run only specific job(s) by name")
def run(only):
    """Run jobs (all or selected)"""
    if only:
        selected = get_job_by_name(only)
        if not selected:
            click.echo("No jobs found matching your selection.")
            return
    else:
        selected = get_all_jobs()

    executor = JobExecutor(selected)
    asyncio.run(executor.run_all())

@cli.command()
def list():
    """List all available jobs"""
    for name, _ in get_all_jobs():
        click.echo(f"- {name}")

if __name__ == "__main__":
    cli()
