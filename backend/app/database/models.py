from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase): pass

class MSMEProfile(Base):
    __tablename__ = "msme_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    msme_id: Mapped[str] = mapped_column(unique=True)
    sector: Mapped[str | None]; provenance: Mapped[str]

class MonthlySnapshot(Base):
    __tablename__ = "monthly_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    msme_id: Mapped[str]; month_index: Mapped[int]
    payload_json: Mapped[str]

class SourceCoverage(Base):
    __tablename__ = "source_coverage"
    id: Mapped[int] = mapped_column(primary_key=True)
    msme_id: Mapped[str]; source: Mapped[str]; available: Mapped[bool]