# AutoGen-Graphiti Architecture Document (Updated)

## Executive Summary

This document describes the refined architecture for a Knowledge Graph-powered AutoGen multi-agent system supporting SME business operations. The system uses FalkorDB/Graphiti to store workflow intelligence and enables AutoGen agents to execute sophisticated business processes through graph queries rather than static CSV files.

## Core Architecture Evolution

### Original Understanding → Current Implementation

**Original Concept**: Import CSV files into a graph database for visualization  
**Current Reality**: Sophisticated multi-tenant, graph-native agent orchestration platform

The architecture has evolved from a simple data import challenge to a comprehensive Knowledge Graph system that:
- Powers AutoGen agents with dynamic workflow intelligence
- Maintains customer-specific knowledge accumulation
- Enables fluid human-agent collaboration
- Supports 30 complex Product Management workflows

## Knowledge Graph Structure (Finalized)

### 1. Core Entity Types

Based on our refined understanding, the Knowledge Graph implements these entity types:

#### Foundation Layer (Shared Across All Customers)
- **BUSINESS_SEGMENT nodes**: Domain containers (Product Management, Operations, Quality Test, Program Management)
- **WORKFLOW_TEMPLATE nodes**: 30 end-to-end business processes
- **TASK_TEMPLATE nodes**: 22 reusable task definitions across 4 roles

#### Customer Execution Layer (Partitioned by customer_id)
- **CUSTOMER nodes**: SME organization instances
- **WORKFLOW_INSTANCE nodes**: Active workflow executions
- **TASK_INSTANCE nodes**: Specific task executions with state
- **WORK_ARTIFACT nodes**: Deliverables with version control

### 2. Relationship Types

The system uses two primary relationship types:
- **USED_IN**: Maps tasks to workflows with orchestration metadata
- **DEPENDS_ON**: Defines task execution dependencies within workflow contexts

## The Five Core CSV Files

Our transformation process produces five essential files for FalkorDB import:

### 1. `business_segments.csv`
```csv
segment_id,segment_name,description,version,node_type
PRODUCT_MANAGEMENT,Product Management,"Customer needs, capabilities, and SME value development",3.0,BUSINESS_SEGMENT
```

### 2. `task_templates.csv`
- **22 task definitions** spanning PRODM (6), BA (7), BSA (4), PRODO (5) roles
- Contains prompts, examples, artifacts, and execution guidance
- Serves as the authoritative Node_ID source

### 3. `workflow_templates.csv`
- **30 workflow definitions** covering the complete product lifecycle:
  - Strategic Planning & Vision (5 workflows)
  - Market & Customer Discovery (5 workflows)
  - Requirements & Analysis (5 workflows)
  - Development & Execution (5 workflows)
  - Release & Deployment (5 workflows)
  - Continuous Improvement & Innovation (5 workflows)

### 4. `task_workflow_relationships.csv`
- Maps tasks to workflows with sequence positions (Start/Early/Mid/Late/End)
- Includes priority scores, notification triggers, and visibility roles
- Enables cross-role coordination

### 5. `task_dependencies.csv`
- Defines prerequisite relationships between tasks
- Scoped to workflow contexts
- Supports Hard and Soft dependency types

## AutoGen Integration Architecture

### Agent Query Patterns

The Knowledge Graph enables these essential AutoGen operations:

#### 1. Task Discovery
```cypher
MATCH (t:TASK_TEMPLATE)-[:USED_IN]->(w:WORKFLOW_INSTANCE)
WHERE t.role = $agent_role 
  AND w.customer_id = $customer_id
  AND w.status = 'active'
RETURN t, w
```

#### 2. Dependency Resolution
```cypher
MATCH (prereq:TASK_TEMPLATE)-[:DEPENDS_ON]->(task:TASK_TEMPLATE)
WHERE task.node_id = $current_task_id
  AND relationship.workflow_context = $workflow_id
RETURN prereq
```

#### 3. Workflow Instantiation
```cypher
MATCH (template:WORKFLOW_TEMPLATE {workflow_id: $workflow_id})
CREATE (instance:WORKFLOW_INSTANCE {
  instance_id: generateId(),
  template_id: $workflow_id,
  customer_id: $customer_id,
  status: 'active',
  created_at: timestamp()
})
RETURN instance
```

### Orchestration Flow Example: "Develop Product Requirements"

When a user selects "develop product requirements":

1. **AutoGen queries** the graph for workflow template REQ_001
2. **System creates** a WORKFLOW_INSTANCE for the customer
3. **First agent (BA)** receives task assignment for BA_WF_001
4. **Downstream agents** get notified of upcoming work
5. **As tasks complete**, dependencies trigger next assignments
6. **Artifacts accumulate** in the customer's knowledge space

## Multi-Tenant Architecture

### Customer Partitioning Strategy

Each SME customer operates within an isolated graph space:
- **Shared Layer**: All customers access the same templates (read-only)
- **Customer Layer**: Execution data partitioned by customer_id
- **No Cross-Contamination**: Queries always include customer context

### Data Model
```typescript
interface CustomerProfile {
  customer_id: string;
  organization_name: string;
  segment_maturity: {
    product_management: "Basic" | "Intermediate" | "Advanced";
  };
  role_mappings: {
    [standard_role: string]: string[];  // Map to customer's org structure
  };
}
```

## Human-Agent Collaboration Patterns

The system supports sophisticated collaboration models:

### 1. Sequential Handoffs
- Agent completes work → Human reviews → Next agent proceeds
- Clear task boundaries with explicit handoff points

### 2. Parallel Collaboration
- Agent prepares foundation while human works on related aspects
- BSA agent can structure technical specs while BA refines requirements

### 3. Adaptive Coordination
- System detects when upstream work is "mature enough" to proceed
- Agents don't wait for formal completion if sufficient context exists

### 4. Queue-Based Notifications
- Humans see tasks assigned to them or requiring their input
- Agents monitor queues for upstream changes requiring attention

## Learning and Memory Architecture

### Artifact Capture
```typescript
interface WorkArtifact {
  artifact_id: string;
  customer_id: string;
  workflow_instance: string;
  task_instance: string;
  artifact_type: string;
  content_reference: string;  // Link to Confluence/Jira
  created_date: Date;
  version: number;
  context_metadata: {
    decisions_made: string[];
    assumptions: string[];
    constraints_identified: string[];
  };
}
```

### Knowledge Accumulation
Over time, the customer's graph accumulates:
- Domain-specific terminology
- Successful workflow patterns
- Team preferences and collaboration styles
- Historical context for decision-making

## Implementation Progress

### Completed
- ✅ All 22 task templates defined with rich examples
- ✅ 13 of 30 workflows transformed (43% complete)
- ✅ Proper graph structure validated
- ✅ No broken references or data integrity issues
- ✅ PRD updated with clear architectural documentation

### In Progress
- 🔄 Workflows 14-30 transformation using established patterns
- 🔄 FalkorDB import scripts development
- 🔄 AutoGen agent query interface design

### Upcoming
- 📅 Multi-tenant customer partitioning implementation
- 📅 Notification system integration
- 📅 Artifact storage with Confluence/Jira
- 📅 Additional business segments (Operations, Quality, Program Management)

## Key Architectural Decisions

### 1. Graph-Native Design
We chose to make AutoGen agents query the graph directly rather than loading CSV files because:
- Enables real-time workflow state management
- Supports dynamic dependency resolution
- Allows cross-workflow intelligence
- Facilitates learning accumulation

### 2. Template-Instance Separation
Separating templates from instances enables:
- Shared best practices across customers
- Customer-specific adaptations
- Clean upgrade paths for workflow improvements
- Historical tracking without template pollution

### 3. Role-Based Task Assignment
Tasks are assigned to roles (PRODM, BA, BSA, PRODO) rather than individuals because:
- Enables flexible team composition
- Supports skill-based routing
- Allows load balancing
- Facilitates coverage during absences

## Success Metrics

The architecture enables these measurable outcomes:
- **30% reduction** in workflow completion time through intelligent coordination
- **40% ROI** through workflow reuse and accumulated knowledge
- **$500/SME** training cost reduction through embedded expertise
- **4-segment coverage** creating competitive differentiation

## Next Steps

1. **Complete Workflow Transformation**: Process remaining 17 workflows
2. **Build Import Pipeline**: Create FalkorDB import scripts with validation
3. **Develop Agent Interfaces**: Build AutoGen query adapters for graph
4. **Test Customer Partitioning**: Validate multi-tenant isolation
5. **Expand to New Segments**: Apply patterns to Operations, Quality, Program Management

## Conclusion

This architecture represents a sophisticated evolution from simple CSV imports to a graph-native, multi-agent orchestration platform. By combining FalkorDB's graph capabilities with AutoGen's agent framework, we're creating a system that doesn't just execute workflows—it learns, adapts, and improves with each customer interaction.

The Knowledge Graph serves as both the intelligence layer and the coordination backbone, enabling SMEs to operate with enterprise-level sophistication while maintaining the agility and personalization their businesses require.