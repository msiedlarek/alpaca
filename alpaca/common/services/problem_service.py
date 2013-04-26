from zope import (
    interface,
    component,
)
import sqlalchemy as sql
from sqlalchemy.orm import exc as db_exc

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.services.interfaces import IProblemService
from alpaca.common.domain.problem import Problem
from alpaca.common.domain.occurrence import Occurrence


@component.adapter(IPersistenceManager)
@interface.implementer(IProblemService)
class ProblemService:

    def __init__(self, persistence_manager):
        self._persistence_manager = persistence_manager

    def create_or_update_problem(self, problem):
        self._persistence_manager.add_if_not_exists(problem, 'hash')
        self._persistence_manager.session.query(
            Problem
        ).filter(
            Problem.hash == problem.hash
        ).update({
            'description': problem.description,
            'last_occurrence': problem.last_occurrence,
            'occurrence_count': self._persistence_manager.session.query(
                Problem.occurrence_count
            ).filter(
                Problem.hash == problem.hash
            ).as_scalar() + 1,
        }, synchronize_session=False)

    def update_problem(self, problem):
        self._persistence_manager.session.add(problem)
        return problem

    def get_problem(self, id):
        try:
            return self._persistence_manager.session.query(
                Problem
            ).filter(
                Problem.id == id
            ).one()
        except db_exc.NoResultFound:
            return None

    def get_problem_by_hash(self, hash):
        try:
            return self._persistence_manager.session.query(
                Problem
            ).filter(
                Problem.hash == hash
            ).one()
        except db_exc.NoResultFound:
            return None

    def get_occurrence(self, id):
        try:
            return self._persistence_manager.session.query(
                Occurrence
            ).filter(
                Occurrence.id == id
            ).one()
        except db_exc.NoResultFound:
            return None

    def create_occurrence_of_problem(self, occurrence, problem_hash):
        occurrence.problem_id = self._persistence_manager.session.query(
            Problem.id
        ).filter(
            Problem.hash == problem_hash
        ).as_scalar()
        self._persistence_manager.session.add(occurrence)
        return occurrence

    def get_environment_problems(self, environment, limit=None):
        query = self._persistence_manager.session.query(
            Problem
        ).distinct().join(
            Occurrence
        ).filter(
            Occurrence.environment == environment
        ).order_by(
            sql.desc(Problem.last_occurrence)
        )
        if limit is not None:
            query = query.limit(limit)
        return query

    def get_problem_occurrence_ids(self, problem):
        return self._persistence_manager.session.query(
            Occurrence.id
        ).filter(
            Occurrence.problem == problem
        ).order_by(
            sql.desc(Occurrence.date)
        )

    def limit_problem_history(self, problem_hash, limit):
        self._persistence_manager.session.query(
            Occurrence
        ).filter(
            Occurrence.id.in_(
                self._persistence_manager.session.query(
                    Occurrence.id
                ).join(
                    Problem
                ).filter(
                    Occurrence.problem_id == Problem.id,
                    Problem.hash == problem_hash,
                ).order_by(
                    sql.desc(Occurrence.date)
                ).offset(
                    limit
                ).subquery()
            )
        ).delete(synchronize_session=False)

    def set_problem_tags(self, problem, tags):
        problem.tags = tags
        self._persistence_manager.session.query(
            Problem
        ).filter(
            Problem.id == problem.id
        ).update({
            'tags': problem.tags,
        }, synchronize_session=False)
