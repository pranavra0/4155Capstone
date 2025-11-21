import pytest
from orchestrator.scheduler import Scheduler
from orchestrator.models import Node, Job


@pytest.fixture
def sample_nodes():
    # Two nodes with different capacities and CPU usage
    return [
        Node(
            id="node1",
            ip="127.0.0.1",
            port=8001,
            cpu=4,
            memory=8192,
            cpu_percent=80.0,  # busier node
        ),
        Node(
            id="node2",
            ip="127.0.0.1",
            port=8002,
            cpu=8,
            memory=16384,
            cpu_percent=20.0,  # more free CPU
        ),
    ]


@pytest.fixture
def sample_job():
    return Job(id="job1", image="nginx", status="pending")


def test_first_fit(sample_job, sample_nodes):
    scheduler = Scheduler(strategy="first_fit")
    chosen = scheduler.schedule_job(job=sample_job, available_nodes=sample_nodes)
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
    # Node2 has much more available CPU (lower cpu_percent)
    assert chosen.id == "node2"


def test_no_nodes(sample_job):
    scheduler = Scheduler()
    chosen = scheduler.schedule_job(sample_job, [])
    assert chosen is None


def test_invalid_strategy(sample_job, sample_nodes):
    scheduler = Scheduler(strategy="does_not_exist")
    with pytest.raises(ValueError):
        scheduler.schedule_job(sample_job, sample_nodes)
