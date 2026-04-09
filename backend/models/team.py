from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    graph_json = Column(Text, nullable=False)  # Serialized ReactFlow graph
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(String(64), primary_key=True, index=True)
    provider = Column(String(64), nullable=False)
    secret_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamRun(Base):
    __tablename__ = "team_runs"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    execution_id = Column(String(64), nullable=False, index=True)
    task_index = Column(Integer, nullable=False)
    task_input = Column(Text, nullable=False)
    final_output = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="completed")
    error_message = Column(Text, nullable=True)
    selected_agent_id = Column(String(255), nullable=True)
    selected_agent = Column(String(255), nullable=True)
    selected_provider = Column(String(64), nullable=True)
    selected_model = Column(String(255), nullable=True)
    routing_reason = Column(Text, nullable=True)
    decision_json = Column(Text, nullable=True)
    routing_json = Column(Text, nullable=True)
    source = Column(String(32), nullable=True, default="task")
    trigger_id = Column(String(255), nullable=True)
    trigger_timestamp = Column(DateTime, nullable=True)
    correlation_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class WebhookTrigger(Base):
    __tablename__ = "webhook_triggers"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(String(255), unique=True, index=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    node_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
