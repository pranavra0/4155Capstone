import pytest
from orchestrator.scheduler import Scheduler
from orchestrator.models import Node, Job

@pytest.fixture
def sample_nodes():
    return [
        Node(id="node1", cpu=4, memory=8192),
        Node(id="node2", cpu=8, memory=16384),
    ]

@pytest.fixture
def sample_job():
    return Job(id="job1", image="nginx", status="pending")

def test_first_fit(sample_job, sample_nodes):
    scheduler = Scheduler(strategy="first_fit")
    chosen = scheduler.schedule_job(sample_job, sample_nodes)
    assert chosen.id == "node1"

def test_round_robin(sample_job, sample_nodes):
    scheduler = Scheduler(strategy="round_robin")
    chosen1 = scheduler.schedule_job(sample_job, sample_nodes)
    chosen2 = scheduler.schedule_job(sample_job, sample_nodes)
    assert chosen1.id == "node1"
    assert chosen2.id == "node2"

def test_resource_aware(sample_job, sample_nodes):
    scheduler = Scheduler(strategy="resource_aware")
    chosen = scheduler.schedule_job(sample_job, sample_nodes)
    assert chosen.id == "node2"  # has more CPU

def test_no_nodes(sample_job):
    scheduler = Scheduler()
    chosen = scheduler.schedule_job(sample_job, [])
    assert chosen is None

def test_invalid_strategy(sample_job, sample_nodes):
    scheduler = Scheduler(strategy="does_not_exist")
    with pytest.raises(ValueError):
        scheduler.schedule_job(sample_job, sample_nodes)

