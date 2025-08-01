import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

Base = declarative_base()

class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    violation_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    bbox = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False)
    camera_id = Column(String(50), default="main")
    location = Column(String(100), default="unknown")
    screenshot_path = Column(String(255))
    processed = Column(Integer, default=0)  # 0: pending, 1: processed, 2: notified

class Statistics(Base):
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    violation_type = Column(String(50), nullable=False)
    count = Column(Integer, default=0)
    shift = Column(String(20), default="all")  # morning, afternoon, night, all

class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///./cctv_monitoring.db"):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True
            )
            
            # Create async session factory
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")
    
    async def add_violation(self, violation_data: Dict[str, Any]) -> int:
        """
        Add a new violation to database
        
        Args:
            violation_data: Dictionary containing violation information
            
        Returns:
            ID of the created violation record
        """
        async with self.async_session() as session:
            try:
                violation = Violation(
                    violation_type=violation_data['type'],
                    timestamp=datetime.fromisoformat(violation_data['timestamp']),
                    bbox=violation_data['bbox'],
                    confidence=violation_data['confidence'],
                    camera_id=violation_data.get('camera_id', 'main'),
                    location=violation_data.get('location', 'unknown'),
                    screenshot_path=violation_data.get('screenshot_path'),
                    processed=0
                )
                
                session.add(violation)
                await session.commit()
                await session.refresh(violation)
                
                logger.info(f"Violation logged: {violation_data['type']} at {violation_data['timestamp']}")
                return violation.id
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error adding violation: {e}")
                raise
    
    async def get_violations(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        violation_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get violations with filters
        
        Args:
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            violation_type: Type of violation to filter
            limit: Maximum number of records to return
            
        Returns:
            List of violation records
        """
        async with self.async_session() as session:
            try:
                query = session.query(Violation)
                
                # Apply filters
                if start_date:
                    start_dt = datetime.fromisoformat(start_date)
                    query = query.filter(Violation.timestamp >= start_dt)
                
                if end_date:
                    end_dt = datetime.fromisoformat(end_date)
                    query = query.filter(Violation.timestamp <= end_dt)
                
                if violation_type:
                    query = query.filter(Violation.violation_type == violation_type)
                
                # Order by timestamp descending and limit
                query = query.order_by(Violation.timestamp.desc()).limit(limit)
                
                violations = await session.execute(query)
                results = []
                
                for violation in violations.scalars():
                    results.append({
                        'id': violation.id,
                        'type': violation.violation_type,
                        'timestamp': violation.timestamp.isoformat(),
                        'bbox': violation.bbox,
                        'confidence': violation.confidence,
                        'camera_id': violation.camera_id,
                        'location': violation.location,
                        'screenshot_path': violation.screenshot_path,
                        'processed': violation.processed
                    })
                
                return results
                
            except Exception as e:
                logger.error(f"Error fetching violations: {e}")
                raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get real-time statistics
        
        Returns:
            Dictionary containing various statistics
        """
        async with self.async_session() as session:
            try:
                # Get today's violations by type
                today = datetime.now().date()
                start_of_day = datetime.combine(today, datetime.min.time())
                end_of_day = datetime.combine(today, datetime.max.time())
                
                # Count violations by type for today
                query = session.query(
                    Violation.violation_type,
                    sa.func.count(Violation.id).label('count')
                ).filter(
                    Violation.timestamp >= start_of_day,
                    Violation.timestamp <= end_of_day
                ).group_by(Violation.violation_type)
                
                result = await session.execute(query)
                today_stats = {row.violation_type: row.count for row in result}
                
                # Get total violations by type
                total_query = session.query(
                    Violation.violation_type,
                    sa.func.count(Violation.id).label('count')
                ).group_by(Violation.violation_type)
                
                total_result = await session.execute(total_query)
                total_stats = {row.violation_type: row.count for row in total_result}
                
                # Get recent violations (last 24 hours)
                yesterday = datetime.now() - timedelta(days=1)
                recent_query = session.query(Violation).filter(
                    Violation.timestamp >= yesterday
                ).order_by(Violation.timestamp.desc()).limit(10)
                
                recent_result = await session.execute(recent_query)
                recent_violations = []
                
                for violation in recent_result.scalars():
                    recent_violations.append({
                        'type': violation.violation_type,
                        'timestamp': violation.timestamp.isoformat(),
                        'confidence': violation.confidence
                    })
                
                return {
                    'today_violations': today_stats,
                    'total_violations': total_stats,
                    'recent_violations': recent_violations,
                    'last_updated': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching statistics: {e}")
                raise
    
    async def update_violation_status(self, violation_id: int, status: int):
        """
        Update violation processing status
        
        Args:
            violation_id: ID of the violation to update
            status: New status (0: pending, 1: processed, 2: notified)
        """
        async with self.async_session() as session:
            try:
                violation = await session.get(Violation, violation_id)
                if violation:
                    violation.processed = status
                    await session.commit()
                    logger.info(f"Updated violation {violation_id} status to {status}")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating violation status: {e}")
                raise
    
    async def get_violation_heatmap(self, days: int = 7) -> Dict[str, Any]:
        """
        Get violation heatmap data for the specified number of days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Heatmap data with location-based violation counts
        """
        async with self.async_session() as session:
            try:
                start_date = datetime.now() - timedelta(days=days)
                
                query = session.query(
                    Violation.location,
                    Violation.violation_type,
                    sa.func.count(Violation.id).label('count')
                ).filter(
                    Violation.timestamp >= start_date
                ).group_by(Violation.location, Violation.violation_type)
                
                result = await session.execute(query)
                
                heatmap_data = {}
                for row in result:
                    location = row.location
                    violation_type = row.violation_type
                    count = row.count
                    
                    if location not in heatmap_data:
                        heatmap_data[location] = {}
                    
                    heatmap_data[location][violation_type] = count
                
                return {
                    'heatmap_data': heatmap_data,
                    'period_days': days,
                    'generated_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error generating heatmap: {e}")
                raise