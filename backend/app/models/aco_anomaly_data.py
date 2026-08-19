from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class AcoAnomalyData(Base):
    __tablename__ = "aco_anomaly_data"

    id = Column(String, primary_key=True)

    aco_id = Column(String, nullable=False)
    performance_year = Column(Integer, nullable=False)

    ed_utilization_change_yoy = Column(Float)
    admission_change_yoy = Column(Float)
    em_utilization_change_yoy = Column(Float)
    advanced_imaging_change_yoy = Column(Float)
    readmission_proxy_rate_yoy_change = Column(Float)
    savings_yoy_change_pct = Column(Float)
    expenditure_variance_pct = Column(Float)
    quality_change_yoy = Column(Float)
    provider_utilization_variation = Column(Float)
    provider_cost_variation = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )