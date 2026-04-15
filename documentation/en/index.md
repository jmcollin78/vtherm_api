# vtherm_api — Documentation

Developer-facing API for building plugins and integrations on top of **Versatile Thermostat** inside Home Assistant.

> **Status**: early stage — interfaces are subject to change.

## Table of contents

- [Overview](overview.md) — what the package does and why it exists
- [Architecture](architecture.md) — components and data flow
- [Getting started](getting-started.md) — installation and first integration
- [API Reference](api-reference.md) — full reference for all public classes and methods
  - [VThermAPI](api-reference.md#vthermapi)
  - [PluginClimate](api-reference.md#pluginclimate)
  - [Interfaces](api-reference.md#interfaces)
  - [Constants and EventType](api-reference.md#constants-and-eventtype)
- [Events reference](events.md) — all VTherm events and their payloads
- [Guides](guides/) — step-by-step recipes for common tasks
  - [Register your integration](guides/register-integration.md)
  - [Listen to thermostat events](guides/listen-to-events.md)
  - [Register a proportional algorithm](guides/proportional-algorithm.md)
  - [Create a FeatureManager](guides/feature-manager.md)
  - [Forward actions to VTherm](guides/forward-actions.md)
- [Testing](testing.md) — patterns for unit and integration tests
