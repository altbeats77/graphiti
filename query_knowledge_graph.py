#!/usr/bin/env python3
"""
promptlyserved Knowledge Graph Query Interface
Easy access to promptlyserved PM workflow architecture in FalkorDB
"""

import redis
import json
from typing import List, Dict, Any


class KnowledgeGraphQuery:
    """Query interface for the Knowledge Graph"""
    
    def __init__(self, host='localhost', port=6379, graph_name='default_db'):
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.graph_name = graph_name
    
    def query(self, cypher_query: str) -> List[Dict]:
        """Execute a Cypher query and return formatted results"""
        try:
            result = self.redis_client.execute_command('GRAPH.QUERY', self.graph_name, cypher_query)
            
            if len(result) < 2:
                return []
            
            headers = result[0]
            rows = result[1]  # FalkorDB returns all rows as a single list
            
            # Convert to list of dictionaries
            formatted_results = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_dict[header] = row[i]
                formatted_results.append(row_dict)
            
            return formatted_results
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def get_all_roles(self) -> List[str]:
        """Get all available roles in the system"""
        results = self.query("MATCH (tt:TASK_TEMPLATE) RETURN DISTINCT tt.role ORDER BY tt.role")
        return [r.get('tt.role', 'Unknown') for r in results if r.get('tt.role')]
    
    def get_tasks_by_role(self, role: str) -> List[Dict]:
        """Get all tasks for a specific role"""
        return self.query(f"""
        MATCH (tt:TASK_TEMPLATE {{role: '{role}'}})
        RETURN tt.node_id, tt.workflow_name, tt.characteristic, tt.prompt_flexibility
        ORDER BY tt.workflow_name
        """)
    
    def get_workflow_details(self, workflow_id: str) -> Dict:
        """Get detailed information about a workflow"""
        results = self.query(f"""
        MATCH (wt:WORKFLOW_TEMPLATE {{workflow_id: '{workflow_id}'}})
        RETURN wt.workflow_name, wt.description, wt.business_value, 
               wt.total_tasks, wt.involved_roles, wt.complexity_level
        """)
        return results[0] if results else {}
    
    def get_workflow_tasks(self, workflow_id: str) -> List[Dict]:
        """Get all tasks used in a specific workflow"""
        return self.query(f"""
        MATCH (tt:TASK_TEMPLATE)-[u:USED_IN]->(wt:WORKFLOW_TEMPLATE {{workflow_id: '{workflow_id}'}})
        RETURN tt.role, tt.workflow_name, tt.characteristic, 
               u.sequence_position, u.priority_score
        ORDER BY u.sequence_position, u.priority_score
        """)
    
    def get_task_dependencies(self, task_id: str) -> List[Dict]:
        """Get dependencies for a specific task"""
        return self.query(f"""
        MATCH (t1:TASK_TEMPLATE {{node_id: '{task_id}'}})-[d:DEPENDS_ON]->(t2:TASK_TEMPLATE)
        RETURN t2.node_id, t2.role, t2.workflow_name, 
               d.dependency_type, d.workflow_context
        ORDER BY d.priority_score
        """)
    
    def find_workflows_by_complexity(self, complexity: str) -> List[Dict]:
        """Find workflows by complexity level"""
        return self.query(f"""
        MATCH (wt:WORKFLOW_TEMPLATE {{complexity_level: '{complexity}'}})
        RETURN wt.workflow_id, wt.workflow_name, wt.total_tasks, wt.involved_roles
        ORDER BY wt.workflow_name
        """)
    
    def get_role_collaboration_map(self) -> List[Dict]:
        """Get which roles work together in workflows"""
        return self.query("""
        MATCH (wt:WORKFLOW_TEMPLATE)
        RETURN wt.workflow_name, wt.involved_roles, wt.complexity_level
        ORDER BY wt.complexity_level, wt.workflow_name
        """)
    
    def search_tasks_by_keyword(self, keyword: str) -> List[Dict]:
        """Search tasks by keyword in name or description"""
        return self.query(f"""
        MATCH (tt:TASK_TEMPLATE)
        WHERE tt.workflow_name CONTAINS '{keyword}' 
           OR tt.characteristic CONTAINS '{keyword}'
           OR tt.keywords_phrases CONTAINS '{keyword}'
        RETURN tt.role, tt.workflow_name, tt.characteristic, tt.keywords_phrases
        ORDER BY tt.role, tt.workflow_name
        """)


def main():
    """Interactive Knowledge Graph explorer"""
    kg = KnowledgeGraphQuery()
    
    print("🚀 promptlyserved Knowledge Graph Query Interface")
    print("=" * 60)
    
    while True:
        print("\nAvailable commands:")
        print("1. List all roles")
        print("2. Get tasks by role")
        print("3. Explore a workflow")
        print("4. Find task dependencies") 
        print("5. Search tasks by keyword")
        print("6. Find workflows by complexity")
        print("7. Custom Cypher query")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            roles = kg.get_all_roles()
            print(f"\n📋 Available roles: {', '.join(roles)}")
            
        elif choice == "2":
            role = input("Enter role (PRODM, BA, BSA, PRODO): ").strip()
            tasks = kg.get_tasks_by_role(role)
            print(f"\n📋 Tasks for {role}:")
            for task in tasks:
                workflow_name = task.get('tt.workflow_name', 'Unknown')
                characteristic = task.get('tt.characteristic', 'Unknown')
                print(f"  • {workflow_name} ({characteristic})")
                
        elif choice == "3":
            workflow_id = input("Enter workflow ID (e.g., LAUNCH_001): ").strip()
            details = kg.get_workflow_details(workflow_id)
            if details:
                workflow_name = details.get('wt.workflow_name', 'Unknown')
                description = details.get('wt.description', 'No description')
                business_value = details.get('wt.business_value', 'No business value')
                complexity = details.get('wt.complexity_level', 'Unknown')
                involved_roles = details.get('wt.involved_roles', 'No roles')
                
                print(f"\n🔄 {workflow_name}")
                print(f"Description: {description}")
                print(f"Business Value: {business_value}")
                print(f"Complexity: {complexity}")
                print(f"Involved Roles: {involved_roles}")
                
                tasks = kg.get_workflow_tasks(workflow_id)
                print(f"\nTasks ({len(tasks)}):")
                for task in tasks:
                    seq_pos = task.get('u.sequence_position', 'N/A')
                    role = task.get('tt.role', 'Unknown')
                    workflow_name = task.get('tt.workflow_name', 'Unknown')
                    print(f"  {seq_pos}: {role} - {workflow_name}")
            else:
                print("Workflow not found")
                
        elif choice == "4":
            task_id = input("Enter task ID (e.g., PRODM_WF_001): ").strip()
            deps = kg.get_task_dependencies(task_id)
            if deps:
                print(f"\n⚡ Dependencies for {task_id}:")
                for dep in deps:
                    role = dep.get('t2.role', 'Unknown')
                    workflow_name = dep.get('t2.workflow_name', 'Unknown')
                    dep_type = dep.get('d.dependency_type', 'Unknown')
                    print(f"  → {role}: {workflow_name} ({dep_type})")
            else:
                print("No dependencies found")
                
        elif choice == "5":
            keyword = input("Enter search keyword: ").strip()
            results = kg.search_tasks_by_keyword(keyword)
            print(f"\n🔍 Search results for '{keyword}':")
            for result in results:
                role = result.get('tt.role', 'Unknown')
                workflow_name = result.get('tt.workflow_name', 'Unknown')
                print(f"  {role}: {workflow_name}")
                
        elif choice == "6":
            complexity = input("Enter complexity (Low, Medium, High): ").strip()
            workflows = kg.find_workflows_by_complexity(complexity)
            print(f"\n🔄 {complexity} complexity workflows:")
            for wf in workflows:
                workflow_id = wf.get('wt.workflow_id', 'Unknown')
                workflow_name = wf.get('wt.workflow_name', 'Unknown')
                total_tasks = wf.get('wt.total_tasks', 'Unknown')
                print(f"  {workflow_id}: {workflow_name} ({total_tasks} tasks)")
                
        elif choice == "7":
            query = input("Enter Cypher query: ").strip()
            results = kg.query(query)
            print(f"\n📊 Query results:")
            for result in results:
                print(f"  {result}")
                
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 