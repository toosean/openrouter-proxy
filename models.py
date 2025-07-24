"""
数据模型和存储
"""
import json
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import os

@dataclass
class RequestRecord:
    """请求记录数据模型"""
    id: str
    timestamp: datetime
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str]
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    response_body: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestRecord':
        """从字典创建实例"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class RequestStorage:
    """请求存储管理器"""
    
    def __init__(self, db_path: str = "proxy_requests.db"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    method TEXT NOT NULL,
                    url TEXT NOT NULL,
                    headers TEXT NOT NULL,
                    body TEXT,
                    authorization_bearer TEXT,
                    response_status INTEGER,
                    response_headers TEXT,
                    response_body TEXT,
                    duration_ms REAL,
                    error TEXT
                )
            ''')
            conn.commit()
    
    def _save_to_database(self, record: RequestRecord):
        """保存请求记录到数据库"""
        try:
            # 提取Authorization Bearer token
            authorization_bearer = None
            if record.headers:
                auth_header = record.headers.get('Authorization') or record.headers.get('authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    authorization_bearer = auth_header[7:]  # 移除 "Bearer " 前缀
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO requests 
                    (id, timestamp, method, url, headers, body, authorization_bearer,
                     response_status, response_headers, response_body, duration_ms, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.id,
                    record.timestamp.isoformat(),
                    record.method,
                    record.url,
                    json.dumps(record.headers) if record.headers else None,
                    record.body,
                    authorization_bearer,
                    record.response_status,
                    json.dumps(record.response_headers) if record.response_headers else None,
                    record.response_body,
                    record.duration_ms,
                    record.error
                ))
                conn.commit()
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    def _load_from_database(self, request_id: str) -> Optional[RequestRecord]:
        """从数据库加载请求记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM requests WHERE id = ?', (request_id,))
                row = cursor.fetchone()
                
                if row:
                    return RequestRecord(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        method=row[2],
                        url=row[3],
                        headers=json.loads(row[4]) if row[4] else {},
                        body=row[5],
                        response_status=row[7],
                        response_headers=json.loads(row[8]) if row[8] else None,
                        response_body=row[9],
                        duration_ms=row[10],
                        error=row[11]
                    )
                return None
        except Exception as e:
            print(f"Error loading from database: {e}")
            return None
    
    def _load_requests_from_database(self, limit: int = 100, offset: int = 0, apikey_filter: str = None) -> List[RequestRecord]:
        """从数据库加载请求列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if apikey_filter:
                    cursor.execute('''
                        SELECT * FROM requests 
                        WHERE authorization_bearer = ?
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    ''', (apikey_filter, limit, offset))
                else:
                    cursor.execute('''
                        SELECT * FROM requests 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    ''', (limit, offset))
                
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    record = RequestRecord(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        method=row[2],
                        url=row[3],
                        headers=json.loads(row[4]) if row[4] else {},
                        body=row[5],
                        response_status=row[7],
                        response_headers=json.loads(row[8]) if row[8] else None,
                        response_body=row[9],
                        duration_ms=row[10],
                        error=row[11]
                    )
                    records.append(record)
                return records
        except Exception as e:
            print(f"Error loading requests from database: {e}")
            return []
    
    def _search_database(self, query: str, limit: int = 100, apikey_filter: str = None) -> List[RequestRecord]:
        """在数据库中搜索请求"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                search_pattern = f'%{query}%'
                
                if apikey_filter:
                    cursor.execute('''
                        SELECT * FROM requests 
                        WHERE (url LIKE ? OR method LIKE ? OR body LIKE ? OR response_body LIKE ?)
                        AND authorization_bearer = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (search_pattern, search_pattern, search_pattern, search_pattern, apikey_filter, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM requests 
                        WHERE url LIKE ? OR method LIKE ? OR body LIKE ? OR response_body LIKE ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (search_pattern, search_pattern, search_pattern, search_pattern, limit))
                
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    record = RequestRecord(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        method=row[2],
                        url=row[3],
                        headers=json.loads(row[4]) if row[4] else {},
                        body=row[5],
                        response_status=row[7],
                        response_headers=json.loads(row[8]) if row[8] else None,
                        response_body=row[9],
                        duration_ms=row[10],
                        error=row[11]
                    )
                    records.append(record)
                return records
        except Exception as e:
            print(f"Error searching database: {e}")
            return []
    
    def _get_total_count_from_database(self, apikey_filter: str = None) -> int:
        """从数据库获取总记录数"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if apikey_filter:
                    cursor.execute('SELECT COUNT(*) FROM requests WHERE authorization_bearer = ?', (apikey_filter,))
                else:
                    cursor.execute('SELECT COUNT(*) FROM requests')
                    
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting count from database: {e}")
            return 0
    
    def add_request(self, method: str, url: str, headers: Dict[str, str], 
                   body: Optional[str] = None) -> str:
        """添加新请求"""
        with self._lock:
            request_id = str(uuid.uuid4())
            record = RequestRecord(
                id=request_id,
                timestamp=datetime.now(),
                method=method,
                url=url,
                headers=headers,
                body=body
            )
            
            # 保存到数据库
            self._save_to_database(record)
            
            return request_id
    
    def update_response(self, request_id: str, status: int, 
                       headers: Dict[str, str], body: Optional[str] = None,
                       duration_ms: Optional[float] = None, error: Optional[str] = None):
        """更新响应信息"""
        with self._lock:
            # 从数据库获取记录
            record = self._load_from_database(request_id)
            if record:
                record.response_status = status
                record.response_headers = headers
                record.response_body = body
                record.duration_ms = duration_ms
                record.error = error
                
                # 更新数据库
                self._save_to_database(record)
    
    def get_request(self, request_id: str) -> Optional[RequestRecord]:
        """获取单个请求记录"""
        with self._lock:
            return self._load_from_database(request_id)
    
    def get_requests(self, limit: int = 100, offset: int = 0, apikey_filter: str = None) -> List[RequestRecord]:
        """获取请求列表"""
        with self._lock:
            return self._load_requests_from_database(limit, offset, apikey_filter)
    
    def get_total_count(self, apikey_filter: str = None) -> int:
        """获取总请求数"""
        with self._lock:
            return self._get_total_count_from_database(apikey_filter)
    
    def search_requests(self, query: str, limit: int = 100, apikey_filter: str = None) -> List[RequestRecord]:
        """搜索请求"""
        with self._lock:
            return self._search_database(query, limit, apikey_filter)

# 全局存储实例
request_storage = RequestStorage()
