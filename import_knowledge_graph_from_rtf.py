#!/usr/bin/env python3
"""
promptlyserved Knowledge Graph RTF Import Script for AutoGen Multi-Agent System
Imports the validated RTF files into FalkorDB for promptlyserved platform
"""

import re
import csv
import json
import redis
import io
from typing import Dict, List, Any, Optional
from datetime import datetime


class RTFKnowledgeGraphImporter:
    """Import Knowledge Graph data from RTF files into FalkorDB"""
    
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
        
    def extract_csv_from_rtf(self, rtf_path: str) -> List[str]:
        """Extract CSV data from RTF file"""
        with open(rtf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the CSV data after the RTF formatting
        # Look for the pattern where actual CSV data starts
        csv_pattern = r'\\strokec2 (.+?)}'
        matches = re.findall(csv_pattern, content, re.DOTALL)
        
        if matches:
            csv_content = matches[0]
            # Replace RTF line breaks with actual newlines
            csv_content = csv_content.replace('\\', '\n')
            # Clean up any remaining RTF artifacts
            csv_content = re.sub(r'[{}]', '', csv_content)
            # Split into lines and filter out empty lines
            lines = [line.strip() for line in csv_content.strip().split('\n') if line.strip()]
            return lines
        
        return []
    
    def execute_cypher(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Execute Cypher query with parameters"""
        try:
            if params is not None:
                # FalkorDB doesn't support parameterized queries the same way
                # So we'll do safe string substitution - order matters for overlapping keys!
                # Sort keys by length (descending) to avoid partial replacements
                sorted_params = sorted(params.items(), key=lambda x: len(x[0]), reverse=True)
                
                for key, value in sorted_params:
                    if isinstance(value, str):
                        # Escape quotes in string values and handle special characters
                        escaped_value = value.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                        query = query.replace(f'${key}', f'"{escaped_value}"')
                    else:
                        query = query.replace(f'${key}', str(value))
            
            result = self.redis_client.execute_command('GRAPH.QUERY', self.graph_name, query)
            return result
        except Exception as e:
            error_msg = f"Query failed: {str(e)}"
            self.stats['errors'].append(f"Query error: {query[:100]} ... - {error_msg}")
            print(f"❌ {error_msg}")
            return []
    
    def import_business_segments(self, rtf_path: str):
        """Import business segment nodes from RTF"""
        print("📊 Importing business segments...")
        
        csv_lines = self.extract_csv_from_rtf(rtf_path)
        if not csv_lines:
            print("❌ No CSV data found in RTF file")
            return
        
        # Parse CSV data
        csv_reader = csv.DictReader(csv_lines)
        
        for row in csv_reader:
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
                'segment_id': row['segment_id'],
                'segment_name': row['segment_name'],
                'description': row['description'],
                'version': row['version'],
                'node_type': row['node_type'],
                'created_at': datetime.now().isoformat()
            }
            
            self.execute_cypher(query, params)
            self.stats['business_segments'] += 1
            print(f"  ✅ {row['segment_name']}")
    
    def import_task_templates(self, rtf_path: str):
        """Import task template nodes from RTF"""
        print("📋 Importing task templates...")
        
        csv_lines = self.extract_csv_from_rtf(rtf_path)
        if not csv_lines:
            print("❌ No CSV data found in RTF file")
            return
        
        # Parse CSV data
        csv_reader = csv.DictReader(csv_lines)
        
        for row in csv_reader:
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
                'node_id': row['node_id'],
                'node_type': row['node_type'],
                'segment_id': row['segment_id'],
                'role': row['role'],
                'workflow_name': row['workflow_name'],
                'characteristic': row['characteristic'],
                'prompt': row['prompt'],
                'pain_point_need': row['pain_point_need'],
                'artifacts': row['artifacts'],
                'keywords_phrases': row['keywords_phrases'],
                'outcomes': row['outcomes'],
                'prompt_flexibility': row['prompt_flexibility'],
                'instruction_with_example': row['instruction_with_example'],
                'example_straightforward': row['example_straightforward'],
                'example_complex': row['example_complex'],
                'example_enterprise': row['example_enterprise'],
                'created_at': datetime.now().isoformat()
            }
            
            self.execute_cypher(query, params)
            self.stats['task_templates'] += 1
            print(f"  ✅ {row['role']}: {row['workflow_name'][:50]}...")
    
    def import_workflow_templates(self, rtf_path: str):
        """Import workflow template nodes from RTF"""
        print("🔄 Importing workflow templates...")
        
        csv_lines = self.extract_csv_from_rtf(rtf_path)
        if not csv_lines:
            print("❌ No CSV data found in RTF file")
            return
        
        # Parse CSV data
        csv_reader = csv.DictReader(csv_lines)
        
        for row in csv_reader:
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
                'workflow_id': row['workflow_id'],
                'node_type': row['node_type'],
                'segment_id': row['segment_id'],
                'workflow_name': row['workflow_name'],
                'description': row['description'],
                'business_value': row['business_value'],
                'total_tasks': int(row['total_tasks']),
                'involved_roles': row['involved_roles'],
                'complexity_level': row['complexity_level'],
                'created_at': datetime.now().isoformat()
            }
            
            self.execute_cypher(query, params)
            self.stats['workflow_templates'] += 1
            print(f"  ✅ {row['workflow_name'][:50]}...")
    
    def import_task_workflow_relationships(self, rtf_path: str):
        """Import USED_IN relationships from RTF"""
        print("🔗 Importing task-workflow relationships...")
        
        csv_lines = self.extract_csv_from_rtf(rtf_path)
        if not csv_lines:
            print("❌ No CSV data found in RTF file")
            return
        
        # Parse CSV data
        csv_reader = csv.DictReader(csv_lines)
        
        for row in csv_reader:
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
                'source_node_id': row['source_node_id'],
                'target_node_id': row['target_node_id'],
                'relationship_type': row['relationship_type'],
                'sequence_position': row['sequence_position'],
                'priority_score': int(row['priority_score']),
                'notification_trigger': row['notification_trigger'],
                'visibility_roles': row['visibility_roles'],
                'created_at': datetime.now().isoformat()
            }
            
            self.execute_cypher(query, params)
            self.stats['used_in_relationships'] += 1
            
            if self.stats['used_in_relationships'] % 25 == 0:
                print(f"  ✅ {self.stats['used_in_relationships']} relationships created...")
    
    def import_task_dependencies(self, rtf_path: str):
        """Import DEPENDS_ON relationships from RTF"""
        print("⚡ Importing task dependencies...")
        
        csv_lines = self.extract_csv_from_rtf(rtf_path)
        if not csv_lines:
            print("❌ No CSV data found in RTF file")
            return
        
        # Parse CSV data
        csv_reader = csv.DictReader(csv_lines)
        
        for row in csv_reader:
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
                'source_node_id': row['source_node_id'],
                'target_node_id': row['target_node_id'],
                'relationship_type': row['relationship_type'],
                'workflow_context': row['workflow_context'],
                'dependency_type': row['dependency_type'],
                'priority_score': int(row['priority_score']),
                'created_at': datetime.now().isoformat()
            }
            
            self.execute_cypher(query, params)
            self.stats['depends_on_relationships'] += 1
            
            if self.stats['depends_on_relationships'] % 25 == 0:
                print(f"  ✅ {self.stats['depends_on_relationships']} dependencies created...")
    
    def create_indexes(self):
        """Create performance indexes"""
        print("🚀 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX FOR (bs:BUSINESS_SEGMENT) ON (bs.segment_id)",
            "CREATE INDEX FOR (tt:TASK_TEMPLATE) ON (tt.node_id)",
            "CREATE INDEX FOR (tt:TASK_TEMPLATE) ON (tt.role)",
            "CREATE INDEX FOR (tt:TASK_TEMPLATE) ON (tt.segment_id)",
            "CREATE INDEX FOR (wt:WORKFLOW_TEMPLATE) ON (wt.workflow_id)",
            "CREATE INDEX FOR (wt:WORKFLOW_TEMPLATE) ON (wt.segment_id)",
            "CREATE INDEX FOR (wt:WORKFLOW_TEMPLATE) ON (wt.complexity_level)",
        ]
        
        for index_query in indexes:
            self.execute_cypher(index_query)
            print("  ✅ Index created")
    
    def verify_import(self):
        """Verify the import was successful"""
        print("🔍 Verifying import...")
        
        # Count nodes
        node_counts = {}
        for node_type in ['BUSINESS_SEGMENT', 'TASK_TEMPLATE', 'WORKFLOW_TEMPLATE']:
            result = self.execute_cypher(f"MATCH (n:{node_type}) RETURN count(n)")
            if result and len(result) > 1:
                node_counts[node_type] = result[1][0]
        
        print("Node counts:")
        for node_type, count in node_counts.items():
            print(f"  {node_type}: {count}")
        
        # Count relationships
        rel_counts = {}
        for rel_type in ['USED_IN', 'DEPENDS_ON']:
            result = self.execute_cypher(f"MATCH ()-[r:{rel_type}]-() RETURN count(r)")
            if result and len(result) > 1:
                rel_counts[rel_type] = result[1][0]
        
        print("Relationship counts:")
        for rel_type, count in rel_counts.items():
            print(f"  {rel_type}: {count}")
    
    def test_autogen_queries(self):
        """Test some AutoGen query patterns"""
        print("🤖 Testing AutoGen query patterns...")
        
        # Test finding tasks by role and workflow
        result = self.execute_cypher("""
        MATCH (tt:TASK_TEMPLATE {role: 'PRODM'})
        MATCH (tt)-[:USED_IN]->(wt:WORKFLOW_TEMPLATE {workflow_id: 'LAUNCH_001'})
        RETURN tt.workflow_name, wt.workflow_name
        """)
        
        if result and len(result) > 1:
            print(f"Sample PRODM tasks in LAUNCH_001: {len(result[1:])} found")
        else:
            print("Sample PRODM tasks in LAUNCH_001: 0 found")
    
    def run_import(self):
        """Run the complete import process"""
        print("🚀 Starting promptlyserved Knowledge Graph import...")
        print(f"📊 Target: {self.graph_name}")
        
        # Import all data
        self.import_business_segments('docs/Product_Management/business_segments_v2.rtf')
        self.import_task_templates('docs/Product_Management/task_templates_v2.rtf')
        self.import_workflow_templates('docs/Product_Management/workflow_templates_v2.rtf')
        self.import_task_workflow_relationships('docs/Product_Management/task_workflow_relationships_v2.rtf')
        self.import_task_dependencies('docs/Product_Management/task_dependencies_v2.rtf')
        
        # Create indexes
        self.create_indexes()
        
        # Show final stats
        print("\n" + "="*60)
        print("📊 promptlyserved KNOWLEDGE GRAPH IMPORT COMPLETE!")
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
        
        # Verify and test
        self.verify_import()
        self.test_autogen_queries()
        
        print("\n✅ promptlyserved Knowledge Graph ready for AutoGen!")


if __name__ == "__main__":
    importer = RTFKnowledgeGraphImporter()
    importer.run_import() 