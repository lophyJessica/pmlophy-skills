# User Story And Acceptance Template

Use this for Jira tickets, Linear issues, backlog refinement, sprint planning, engineering handoff, and QA preparation.

## Ticket Shape

- Title:
- User story:
- Context:
- Problem:
- Goal:
- Priority:
- Owner:
- Dependencies:

## User Story

Write as:

As a [user or role], I want to [action], so that [outcome].

Prefer real roles over generic "user" when possible.

## Functional Requirements

Use specific behavior:
- Inputs:
- Outputs:
- States:
- Permissions:
- Limits:
- Error handling:
- Data persistence:

## Acceptance Criteria

Use Given/When/Then for behavior with clear state transitions.

Example:
- Given [precondition], when [action], then [expected result].

For simpler work, use checklist criteria:
- The user can...
- The system displays...
- The system prevents...
- The event is logged when...

## Edge Cases

Cover:
- Empty or missing data
- Invalid input
- Slow or failed network
- Permission denied
- Duplicate action
- Partial success
- Mobile layout
- Localization or timezone issues when relevant

## Analytics

- Event name:
- Trigger:
- Properties:
- Success metric affected:

## QA Notes

- Main happy path:
- Regression areas:
- Test data needed:
- Browser, device, or environment coverage:

## Engineering Notes

Include only when useful:
- API changes:
- Data model:
- Migration:
- Feature flag:
- Backward compatibility:
- Security or privacy:
