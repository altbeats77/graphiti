#!/usr/bin/env python3
"""
Knowledge Graph Import Script for AutoGen Multi-Agent System
Imports the new PM workflow architecture into FalkorDB
"""

import csv
import json
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime


class KnowledgeGraphImporter:
    """Import Knowledge Graph data into FalkorDB for AutoGen orchestration"""
    
    def __init__(self, host='localhost', port=6379, graph_name='default_db'):
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.graph_name = graph_name
        self.stats = {
            'business_segments': 0,
            'task_templates': 0,
            'workflow_templates': 0,
            'used_in_relationships': 0,
            'depends_on_relationships': 0,
            'errors': []
        }
    
    def execute_cypher(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Execute Cypher query with parameters"""
        try:
            if params is not None:
                # Convert params to the format FalkorDB expects
                formatted_params = []
                for key, value in params.items():
                    if isinstance(value, str):
                        formatted_params.append(f'{key}="{value}"')
                    elif isinstance(value, list):
                        # Handle arrays - convert to comma-separated strings for now
                        formatted_params.append(f'{key}="{",".join(map(str, value))}"')
                    else:
                        formatted_params.append(f'{key}={value}')
                
                query_with_params = f"CYPHER {' '.join(formatted_params)} {query}"
            else:
                query_with_params = query
            
            result = self.redis_client.execute_command('GRAPH.QUERY', self.graph_name, query_with_params)
            return result
        except Exception as e:
            self.stats['errors'].append(f"Query error: {query[:100]}... - {str(e)}")
            print(f"❌ Query failed: {e}")
            return []
    
    def import_business_segments(self, csv_path: str):
        """Import business segment nodes"""
        print("📊 Importing business segments...")
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Clean BOM from fieldnames if present
            if reader.fieldnames:
                reader.fieldnames = [name.lstrip('\ufeff') for name in reader.fieldnames]
            
            for row in reader:
                # Clean BOM from keys if present
                clean_row = {key.lstrip('\ufeff'): value for key, value in row.items()}
                
                query = """
                CREATE (bs:BUSINESS_SEGMENT {
                    segment_id: $segment_id,
                    segment_name: $segment_name,
                    description: $description,
                    version: $version,
                    node_type: $node_type,
                    created_at: $created_at
                })
                """
                
                params = {
                    'segment_id': clean_row['segment_id'],
                    'segment_name': clean_row['segment_name'],
                    'description': clean_row['description'],
                    'version': clean_row['version'],
                    'node_type': clean_row['node_type'],
                    'created_at': datetime.now().isoformat()
                }
                
                self.execute_cypher(query, params)
                self.stats['business_segments'] += 1
                print(f"  ✅ {clean_row['segment_name']}")
    
    def import_task_templates(self, csv_path: str):
        """Import task template nodes"""
        print("📋 Importing task templates...")
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Clean BOM from fieldnames if present
            if reader.fieldnames:
                reader.fieldnames = [name.lstrip('\ufeff') for name in reader.fieldnames]
            
            for row in reader:
                # Clean BOM from keys if present
                clean_row = {key.lstrip('\ufeff'): value for key, value in row.items()}
                
                query = """
                CREATE (tt:TASK_TEMPLATE {
                    node_id: $node_id,
                    node_type: $node_type,
                    segment_id: $segment_id,
                    role: $role,
                    workflow_name: $workflow_name,
                    characteristic: $characteristic,
                    prompt: $prompt,
                    pain_point_need: $pain_point_need,
                    artifacts: $artifacts,
                    keywords_phrases: $keywords_phrases,
                    outcomes: $outcomes,
                    prompt_flexibility: $prompt_flexibility,
                    instruction_with_example: $instruction_with_example,
                    example_straightforward: $example_straightforward,
                    example_complex: $example_complex,
                    example_enterprise: $example_enterprise,
                    created_at: $created_at
                })
                """
                
                params = {
                    'node_id': clean_row['node_id'],
                    'node_type': clean_row['node_type'],
                    'segment_id': clean_row['segment_id'],
                    'role': clean_row['role'],
                    'workflow_name': clean_row['workflow_name'],
                    'characteristic': clean_row['characteristic'],
                    'prompt': clean_row['prompt'],
                    'pain_point_need': clean_row['pain_point_need'],
                    'artifacts': clean_row['artifacts'],
                    'keywords_phrases': clean_row['keywords_phrases'],
                    'outcomes': clean_row['outcomes'],
                    'prompt_flexibility': clean_row['prompt_flexibility'],
                    'instruction_with_example': clean_row['instruction_with_example'],
                    'example_straightforward': clean_row['example_straightforward'],
                    'example_complex': clean_row['example_complex'],
                    'example_enterprise': clean_row['example_enterprise'],
                    'created_at': datetime.now().isoformat()
                }
                
                self.execute_cypher(query, params)
                self.stats['task_templates'] += 1
                print(f"  ✅ {clean_row['role']}: {clean_row['workflow_name'][:50]}...")
    
    def import_workflow_templates(self, csv_path: str):
        """Import workflow template nodes"""
        print("🔄 Importing workflow templates...")
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Clean BOM from fieldnames if present
            if reader.fieldnames:
                reader.fieldnames = [name.lstrip('\ufeff') for name in reader.fieldnames]
            
            for row in reader:
                # Clean BOM from keys if present
                clean_row = {key.lstrip('\ufeff'): value for key, value in row.items()}
                
                query = """
                CREATE (wt:WORKFLOW_TEMPLATE {
                    workflow_id: $workflow_id,
                    node_type: $node_type,
                    segment_id: $segment_id,
                    workflow_name: $workflow_name,
                    description: $description,
                    business_value: $business_value,
                    total_tasks: $total_tasks,
                    involved_roles: $involved_roles,
                    complexity_level: $complexity_level,
                    created_at: $created_at
                })
                """
                
                params = {
                    'workflow_id': clean_row['workflow_id'],
                    'node_type': clean_row['node_type'],
                    'segment_id': clean_row['segment_id'],
                    'workflow_name': clean_row['workflow_name'],
                    'description': clean_row['description'],
                    'business_value': clean_row['business_value'],
                    'total_tasks': int(clean_row['total_tasks']),
                    'involved_roles': clean_row['involved_roles'],
                    'complexity_level': clean_row['complexity_level'],
                    'created_at': datetime.now().isoformat()
                }
                
                self.execute_cypher(query, params)
                self.stats['workflow_templates'] += 1
                print(f"  ✅ {clean_row['workflow_name'][:50]}...")
    
    def import_task_workflow_relationships(self, csv_path: str):
        """Import USED_IN relationships between tasks and workflows"""
        print("🔗 Importing task-workflow relationships...")
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Clean BOM from fieldnames if present
            if reader.fieldnames:
                reader.fieldnames = [name.lstrip('\ufeff') for name in reader.fieldnames]
            
            for row in reader:
                # Clean BOM from keys if present
                clean_row = {key.lstrip('\ufeff'): value for key, value in row.items()}
                
                query = """
                MATCH (tt:TASK_TEMPLATE {node_id: $source_node_id})
                MATCH (wt:WORKFLOW_TEMPLATE {workflow_id: $target_node_id})
                CREATE (tt)-[r:USED_IN {
                    relationship_type: $relationship_type,
                    sequence_position: $sequence_position,
                    priority_score: $priority_score,
                    notification_trigger: $notification_trigger,
                    visibility_roles: $visibility_roles,
                    created_at: $created_at
                }]->(wt)
                """
                
                params = {
                    'source_node_id': clean_row['source_node_id'],
                    'target_node_id': clean_row['target_node_id'],
                    'relationship_type': clean_row['relationship_type'],
                    'sequence_position': clean_row['sequence_position'],
                    'priority_score': int(clean_row['priority_score']),
                    'notification_trigger': clean_row['notification_trigger'],
                    'visibility_roles': clean_row['visibility_roles'],
                    'created_at': datetime.now().isoformat()
                }
                
                self.execute_cypher(query, params)
                self.stats['used_in_relationships'] += 1
                
                if self.stats['used_in_relationships'] % 25 == 0:
                    print(f"  ✅ {self.stats['used_in_relationships']} relationships created...")
    
    def import_task_dependencies(self, csv_path: str):
        """Import DEPENDS_ON relationships between tasks"""
        print("⚡ Importing task dependencies...")
        
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Clean BOM from fieldnames if present
            if reader.fieldnames:
                reader.fieldnames = [name.lstrip('\ufeff') for name in reader.fieldnames]
            
            for row in reader:
                # Clean BOM from keys if present
                clean_row = {key.lstrip('\ufeff'): value for key, value in row.items()}
                
                query = """
                MATCH (tt1:TASK_TEMPLATE {node_id: $source_node_id})
                MATCH (tt2:TASK_TEMPLATE {node_id: $target_node_id})
                CREATE (tt1)-[r:DEPENDS_ON {
                    relationship_type: $relationship_type,
                    workflow_context: $workflow_context,
                    dependency_type: $dependency_type,
                    priority_score: $priority_score,
                    created_at: $created_at
                }]->(tt2)
                """
                
                params = {
                    'source_node_id': clean_row['source_node_id'],
                    'target_node_id': clean_row['target_node_id'],
                    'relationship_type': clean_row['relationship_type'],
                    'workflow_context': clean_row['workflow_context'],
                    'dependency_type': clean_row['dependency_type'],
                    'priority_score': int(clean_row['priority_score']),
                    'created_at': datetime.now().isoformat()
                }
                
                self.execute_cypher(query, params)
                self.stats['depends_on_relationships'] += 1
                
                if self.stats['depends_on_relationships'] % 25 == 0:
                    print(f"  ✅ {self.stats['depends_on_relationships']} dependencies created...")
    
    def create_indexes(self):
        """Create performance indexes for AutoGen queries"""
        print("🚀 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX FOR (n:TASK_TEMPLATE) ON (n.node_id)",
            "CREATE INDEX FOR (n:TASK_TEMPLATE) ON (n.role)",
            "CREATE INDEX FOR (n:TASK_TEMPLATE) ON (n.segment_id)",
            "CREATE INDEX FOR (n:WORKFLOW_TEMPLATE) ON (n.workflow_id)",
            "CREATE INDEX FOR (n:WORKFLOW_TEMPLATE) ON (n.segment_id)",
            "CREATE INDEX FOR (n:WORKFLOW_TEMPLATE) ON (n.complexity_level)",
            "CREATE INDEX FOR (n:BUSINESS_SEGMENT) ON (n.segment_id)",
            "CREATE INDEX FOR ()-[r:USED_IN]-() ON (r.sequence_position)",
            "CREATE INDEX FOR ()-[r:DEPENDS_ON]-() ON (r.workflow_context)",
            "CREATE INDEX FOR ()-[r:DEPENDS_ON]-() ON (r.dependency_type)"
        ]
        
        for index_query in indexes:
            try:
                self.execute_cypher(index_query)
                print(f"  ✅ Index created")
            except Exception as e:
                # Index might already exist
                print(f"  ⚠️  Index creation: {e}")
    
    def run_import(self):
        """Execute the complete import process"""
        print("🚀 Starting Knowledge Graph import...")
        print(f"📊 Target: {self.graph_name}")
        
        # Import nodes first
        self.import_business_segments('docs/Product_Management/business_segments_v2.csv')
        self.import_task_templates('docs/Product_Management/task_templates_v2.csv')
        self.import_workflow_templates('docs/Product_Management/workflow_templates_v2.csv')
        
        # Import relationships
        self.import_task_workflow_relationships('docs/Product_Management/task_workflow_relationships_v2.csv')
        self.import_task_dependencies('docs/Product_Management/task_dependencies_v2.csv')
        
        # Create indexes for performance
        self.create_indexes()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 IMPORT COMPLETE!")
        print("="*60)
        print(f"Business Segments: {self.stats['business_segments']}")
        print(f"Task Templates: {self.stats['task_templates']}")
        print(f"Workflow Templates: {self.stats['workflow_templates']}")
        print(f"USED_IN Relationships: {self.stats['used_in_relationships']}")
        print(f"DEPENDS_ON Relationships: {self.stats['depends_on_relationships']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        # Verify the import
        self.verify_import()
    
    def verify_import(self):
        """Verify the import was successful"""
        print("\n🔍 Verifying import...")
        
        # Check node counts
        node_counts = self.redis_client.execute_command('GRAPH.QUERY', self.graph_name, 
            'MATCH (n) RETURN labels(n)[0] as type, count(n) as count')
        
        print("Node counts:")
        for row in node_counts[1]:
            print(f"  {row[0]}: {row[1]}")
        
        # Check relationship counts
        rel_counts = self.redis_client.execute_command('GRAPH.QUERY', self.graph_name,
            'MATCH ()-[r]->() RETURN type(r) as type, count(r) as count')
        
        print("Relationship counts:")
        for row in rel_counts[1]:
            print(f"  {row[0]}: {row[1]}")
        
        # Test a sample AutoGen query
        print("\n🤖 Testing AutoGen query patterns...")
        
        # Query for PRODM tasks in LAUNCH_001 workflow
        test_query = """
        MATCH (t:TASK_TEMPLATE)-[r:USED_IN]->(w:WORKFLOW_TEMPLATE)
        WHERE t.role = 'PRODM' AND w.workflow_id = 'LAUNCH_001'
        RETURN t.node_id, r.sequence_position, t.workflow_name
        ORDER BY r.sequence_position
        """
        
        result = self.redis_client.execute_command('GRAPH.QUERY', self.graph_name, test_query)
        print(f"Sample PRODM tasks in LAUNCH_001: {len(result[1])} found")
        
        print("\n✅ promptlyserved Knowledge Graph ready for AutoGen!")


if __name__ == "__main__":
    importer = KnowledgeGraphImporter()
    importer.run_import() 