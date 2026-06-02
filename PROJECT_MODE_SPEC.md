# PROJECT_MODE_SPEC.md

# ROBIN AI — Project Intelligence Layer Specification

Version: 1.0

Status: Design Phase

---

# Purpose

Project Mode allows ROBIN to transition from a conversational assistant into a project operator.

Instead of discussing projects, ROBIN should:

* structure projects
* collect requirements
* maintain project continuity
* coordinate workflows
* prepare Antigravity prompts
* manage project sessions

ROBIN remains the planner.

Antigravity remains the builder.

---

# Core Philosophy

ROBIN should never become a code generator.

ROBIN should become:

* planner
* architect
* coordinator
* operator

The actual implementation work may be delegated to:

* Antigravity
* development tools
* IDEs
* external systems

---

# Project Mode Lifecycle

Project Mode has six stages.

## Stage 1 — Project Detection

Triggered when the user expresses build intent.

Examples:

* let's build
* let's create
* start a project
* make a website
* build an app
* build a game
* create a dashboard
* create a startup

ROBIN should detect intent and enter Project Mode.

---

## Stage 2 — Requirement Intake

ROBIN gathers essential information.

Questions should be adaptive.

Examples:

Website:

* target audience
* business type
* design style
* required pages
* authentication needs

Mobile App:

* platform
* user type
* key features
* monetization model

AI Project:

* objective
* data source
* model requirements
* deployment target

Questions should feel conversational.

Never interrogate the user with giant forms.

---

## Stage 3 — Project Structuring

ROBIN organizes collected information into:

Project Summary

Project Goals

Core Features

Suggested Architecture

Suggested Tech Stack

Build Roadmap

Risks

Future Expansion Ideas

---

## Stage 4 — Architecture Planning

ROBIN proposes:

* frontend architecture
* backend architecture
* database strategy
* integrations
* deployment approach

The goal is guidance.

Not implementation.

---

## Stage 5 — Antigravity Handoff

After enough information is collected:

ROBIN prepares:

Antigravity Build Prompt

The prompt should contain:

* project context
* requirements
* architecture
* feature list
* implementation expectations

ROBIN may optionally open Antigravity automatically in future phases.

---

## Stage 6 — Active Project Session

Project becomes active.

ROBIN tracks:

* current phase
* architecture decisions
* completed milestones
* pending tasks
* known issues

This enables project continuity.

---

# Project States

Each project exists in one state.

States:

PLANNING

DESIGNING

BUILDING

TESTING

REFINING

DEPLOYING

MAINTAINING

ARCHIVED

Only one primary state should be active at a time.

---

# Project Metadata

Each project should store:

Project Name

Project Type

Created Date

Last Active Date

Status

Summary

Features

Tech Stack

Architecture Notes

Current Milestone

Open Tasks

Antigravity Prompts

Session History

---

# Project Categories

Initial supported categories:

Website

Mobile App

Desktop App

AI Assistant

Automation Tool

SaaS Product

Dashboard

Game

Startup Idea

General Software Project

Future categories may be added later.

---

# Project Continuity Rules

ROBIN should support:

continue project

resume build

switch project

show status

show roadmap

what's next

project summary

ROBIN should restore context without requiring full recap.

---

# Project Switching

Example:

switch to ROBIN project

switch to gym website

continue dashboard

ROBIN should activate the selected project and load its context.

---

# Antigravity Relationship

ROBIN is:

Planner

Architect

Coordinator

Operator

Antigravity is:

Builder

Generator

Implementation Engine

ROBIN should prepare work.

Antigravity should execute work.

---

# User Experience Goal

Target interaction:

User:
"Let's build a website."

ROBIN:
"Alright, boss.

Opening Project Mode.

What are we building?

• Portfolio
• SaaS
• E-commerce
• Dashboard
• AI Product"

After gathering information:

ROBIN:
"Project Summary Ready.

Architecture Suggested.

Antigravity Prompt Prepared."

This should feel like working with a technical partner rather than chatting with an AI.

---

# Success Criteria

Project Mode succeeds when:

* build intent is detected reliably
* requirements are gathered naturally
* architecture is organized clearly
* projects persist across sessions
* Antigravity prompts are generated consistently
* project continuity feels effortless

Final Goal:

Transform ROBIN from a conversational assistant into a project operating system.
