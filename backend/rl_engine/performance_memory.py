import json
import sqlite3
import os
import statistics
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

class PerformanceMemory:
    """
    Maintains rolling history of reward scores per agent.
    Adjusts future confidence weighting using reward average.
    Uses SQLITE/JSON storage for lightweight persistence.
    """
    
    def __init__(self, db_path: str = "performance_memory.db", json_path: str = "performance_memory.json"):
        self.db_path = db_path
        self.json_path = json_path
        self.use_sqlite = True  # Flag to toggle between SQLite and JSON storage
        
        # Initialize storage
        if self.use_sqlite:
            self._init_sqlite_db()
        else:
            self._init_json_storage()
    
    def _init_sqlite_db(self):
        """
        Initialize SQLite database for performance memory.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for storing performance records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                jurisdiction TEXT,
                reward_score REAL NOT NULL,
                confidence_before REAL,
                confidence_after REAL,
                timestamp TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_id ON performance_records(agent_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trace_id ON performance_records(trace_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_json_storage(self):
        """
        Initialize JSON storage for performance memory.
        """
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump({}, f)
    
    def record_performance(self, trace_id: str, agent_id: str, jurisdiction: str, 
                         reward_score: float, confidence_before: float, confidence_after: float,
                         details: Dict[str, Any] = None):
        """
        Record a performance entry.
        
        Args:
            trace_id: Trace ID linking to the response
            agent_id: ID of the agent
            jurisdiction: Jurisdiction of the agent
            reward_score: Computed reward score
            confidence_before: Confidence score before feedback
            confidence_after: Confidence score after feedback adjustment
            details: Additional details about the performance
        """
        timestamp = datetime.utcnow().isoformat()
        
        if self.use_sqlite:
            self._record_sqlite(trace_id, agent_id, jurisdiction, reward_score, 
                              confidence_before, confidence_after, timestamp, details)
        else:
            self._record_json(trace_id, agent_id, jurisdiction, reward_score, 
                            confidence_before, confidence_after, timestamp, details)
    
    def _record_sqlite(self, trace_id: str, agent_id: str, jurisdiction: str,
                      reward_score: float, confidence_before: float, confidence_after: float,
                      timestamp: str, details: Dict[str, Any] = None):
        """
        Record performance in SQLite database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_records 
            (trace_id, agent_id, jurisdiction, reward_score, confidence_before, 
             confidence_after, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (trace_id, agent_id, jurisdiction, reward_score, confidence_before,
              confidence_after, timestamp, json.dumps(details) if details else None))
        
        conn.commit()
        conn.close()
    
    def _record_json(self, trace_id: str, agent_id: str, jurisdiction: str,
                    reward_score: float, confidence_before: float, confidence_after: float,
                    timestamp: str, details: Dict[str, Any] = None):
        """
        Record performance in JSON file.
        """
        data = self._load_json_data()
        
        if trace_id not in data:
            data[trace_id] = []
            
        data[trace_id].append({
            "agent_id": agent_id,
            "jurisdiction": jurisdiction,
            "reward_score": reward_score,
            "confidence_before": confidence_before,
            "confidence_after": confidence_after,
            "timestamp": timestamp,
            "details": details
        })
        
        self._save_json_data(data)
    
    def get_agent_performance_history(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get performance history for a specific agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of records to return
            
        Returns:
            List of performance records
        """
        if self.use_sqlite:
            return self._get_agent_history_sqlite(agent_id, limit)
        else:
            return self._get_agent_history_json(agent_id, limit)
    
    def _get_agent_history_sqlite(self, agent_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get agent performance history from SQLite.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM performance_records 
            WHERE agent_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (agent_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def _get_agent_history_json(self, agent_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get agent performance history from JSON.
        """
        data = self._load_json_data()
        records = []
        
        for trace_id, trace_records in data.items():
            for record in trace_records:
                if record.get("agent_id") == agent_id:
                    record["trace_id"] = trace_id
                    records.append(record)
        
        # Sort by timestamp and limit
        records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return records[:limit]
    
    def calculate_agent_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """
        Calculate performance metrics for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary of performance metrics
        """
        history = self.get_agent_performance_history(agent_id, 1000)  # Get substantial history
        
        if not history:
            return {
                "agent_id": agent_id,
                "total_interactions": 0,
                "average_reward": 0.0,
                "success_rate": 0.0,
                "recent_trend": "insufficient_data"
            }
        
        total_interactions = len(history)
        total_reward = sum(record["reward_score"] for record in history)
        average_reward = total_reward / total_interactions
        
        # Success rate (positive rewards)
        successful_interactions = sum(1 for record in history if record["reward_score"] > 0)
        success_rate = successful_interactions / total_interactions
        
        # Recent trend (compare last 10% with first 10%)
        sample_size = max(5, total_interactions // 10)
        if sample_size * 2 <= total_interactions:
            recent_avg = sum(record["reward_score"] for record in history[:sample_size]) / sample_size
            older_avg = sum(record["reward_score"] for record in history[-sample_size:]) / sample_size
            
            if recent_avg > older_avg + 0.1:
                trend = "improving"
            elif recent_avg < older_avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "agent_id": agent_id,
            "total_interactions": total_interactions,
            "average_reward": average_reward,
            "success_rate": success_rate,
            "recent_trend": trend
        }
    
    def adjust_confidence_based_on_performance(self, agent_id: str, base_confidence: float) -> float:
        """
        Adjust confidence score based on agent's performance history.
        
        Args:
            agent_id: ID of the agent
            base_confidence: Original confidence score
            
        Returns:
            Adjusted confidence score
        """
        metrics = self.calculate_agent_performance_metrics(agent_id)
        
        # If no history, return base confidence
        if metrics["total_interactions"] == 0:
            return base_confidence
        
        # Adjust based on average reward
        reward_factor = (metrics["average_reward"] + 1) / 2  # Normalize from [-1,1] to [0,1]
        
        # Adjust based on success rate
        success_factor = metrics["success_rate"]
        
        # Weighted adjustment
        adjusted_confidence = (
            0.5 * base_confidence +
            0.3 * reward_factor +
            0.2 * success_factor
        )
        
        # Ensure result is within bounds
        return max(0.0, min(1.0, adjusted_confidence))
    
    def _load_json_data(self) -> Dict[str, Any]:
        """
        Load data from JSON file.
        """
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json_data(self, data: Dict[str, Any]):
        """
        Save data to JSON file.
        """
        try:
            with open(self.json_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # In a real system, we'd log this error
    
    def export_to_json(self, filepath: str = None) -> str:
        """
        Export all performance data to JSON.
        
        Args:
            filepath: Optional path to save file
            
        Returns:
            JSON string of all data
        """
        if self.use_sqlite:
            data = self._export_sqlite_to_dict()
        else:
            data = self._load_json_data()
        
        json_str = json.dumps(data, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def _export_sqlite_to_dict(self) -> Dict[str, Any]:
        """
        Export SQLite data to dictionary format.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM performance_records')
        rows = cursor.fetchall()
        conn.close()
        
        # Group by trace_id
        data = {}
        for row in rows:
            trace_id = row["trace_id"]
            if trace_id not in data:
                data[trace_id] = []
            
            record = dict(row)
            # Parse details JSON if present
            if record["details"]:
                try:
                    record["details"] = json.loads(record["details"])
                except json.JSONDecodeError:
                    pass  # Keep as string if parsing fails
            
            # Remove trace_id from record since it's the key
            del record["trace_id"]
            data[trace_id].append(record)
        
        return data
    
    def clear_performance_data(self):
        """
        Clear all performance data.
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM performance_records')
            conn.commit()
            conn.close()
        else:
            with open(self.json_path, 'w') as f:
                json.dump({}, f)

    def get_rolling_stats(self, agent_id: str, window_hours: int = 24) -> Dict[str, Any]:
        """
        Get rolling statistics for an agent over the specified time window.

        Args:
            agent_id: ID of the agent
            window_hours: Time window in hours for rolling statistics

        Returns:
            Dictionary containing mean, variance, and confidence trend
        """
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
        cutoff_iso = cutoff_time.isoformat()

        if self.use_sqlite:
            return self._get_rolling_stats_sqlite(agent_id, cutoff_iso)
        else:
            return self._get_rolling_stats_json(agent_id, cutoff_iso)

    def _get_rolling_stats_sqlite(self, agent_id: str, cutoff_iso: str) -> Dict[str, Any]:
        """Get rolling stats from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT reward_score, confidence_before, confidence_after, timestamp
            FROM performance_records
            WHERE agent_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (agent_id, cutoff_iso))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                "agent_id": agent_id,
                "window_hours": 24,
                "sample_count": 0,
                "mean_reward": 0.0,
                "variance_reward": 0.0,
                "confidence_trend": "insufficient_data"
            }

        rewards = [row[0] for row in rows]
        confidences_before = [row[1] for row in rows if row[1] is not None]
        confidences_after = [row[2] for row in rows if row[2] is not None]

        # Calculate statistics
        mean_reward = statistics.mean(rewards)
        variance_reward = statistics.variance(rewards) if len(rewards) > 1 else 0.0

        # Confidence trend analysis
        if len(confidences_before) > 1 and len(confidences_after) > 1:
            avg_conf_before = statistics.mean(confidences_before)
            avg_conf_after = statistics.mean(confidences_after)

            if avg_conf_after > avg_conf_before + 0.05:
                confidence_trend = "increasing"
            elif avg_conf_after < avg_conf_before - 0.05:
                confidence_trend = "decreasing"
            else:
                confidence_trend = "stable"
        else:
            confidence_trend = "insufficient_data"

        return {
            "agent_id": agent_id,
            "window_hours": 24,
            "sample_count": len(rewards),
            "mean_reward": round(mean_reward, 4),
            "variance_reward": round(variance_reward, 4),
            "confidence_trend": confidence_trend
        }

    def _get_rolling_stats_json(self, agent_id: str, cutoff_iso: str) -> Dict[str, Any]:
        """Get rolling stats from JSON."""
        data = self._load_json_data()
        rewards = []
        confidences_before = []
        confidences_after = []

        for trace_id, trace_records in data.items():
            for record in trace_records:
                if (record.get("agent_id") == agent_id and
                    record.get("timestamp", "") >= cutoff_iso):
                    rewards.append(record["reward_score"])
                    if record.get("confidence_before") is not None:
                        confidences_before.append(record["confidence_before"])
                    if record.get("confidence_after") is not None:
                        confidences_after.append(record["confidence_after"])

        if not rewards:
            return {
                "agent_id": agent_id,
                "window_hours": 24,
                "sample_count": 0,
                "mean_reward": 0.0,
                "variance_reward": 0.0,
                "confidence_trend": "insufficient_data"
            }

        # Calculate statistics
        mean_reward = statistics.mean(rewards)
        variance_reward = statistics.variance(rewards) if len(rewards) > 1 else 0.0

        # Confidence trend analysis
        if len(confidences_before) > 1 and len(confidences_after) > 1:
            avg_conf_before = statistics.mean(confidences_before)
            avg_conf_after = statistics.mean(confidences_after)

            if avg_conf_after > avg_conf_before + 0.05:
                confidence_trend = "increasing"
            elif avg_conf_after < avg_conf_before - 0.05:
                confidence_trend = "decreasing"
            else:
                confidence_trend = "stable"
        else:
            confidence_trend = "insufficient_data"

        return {
            "agent_id": agent_id,
            "window_hours": 24,
            "sample_count": len(rewards),
            "mean_reward": round(mean_reward, 4),
            "variance_reward": round(variance_reward, 4),
            "confidence_trend": confidence_trend
        }