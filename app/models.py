from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint
from app import bcrypt


class Moallim(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    its: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), unique=True)
    # darajah: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    daurs = relationship("Daur", back_populates="moallim")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Moallim {self.name}>"


class Daur(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    moallim_id: Mapped[int] = mapped_column(Integer, ForeignKey(Moallim.id))

    # Relationships
    moallim: Mapped[Moallim] = relationship(back_populates="daurs")
    students = relationship(
        "Student", back_populates="daur", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f"<Daur {self.name}>"


class Student(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    its: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(64))
    grade: Mapped[str] = mapped_column(String(1))
    daur_id: Mapped[int] = mapped_column(Integer, ForeignKey(Daur.id))

    # Composite unique constraint

    __table_args__ = (UniqueConstraint("its", "daur_id", name="uix_its_daur"),)

    # Relationships
    daur = relationship("Daur", back_populates="students")

    def __repr__(self):
        return f"<Student {self.name}>"
