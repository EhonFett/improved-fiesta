"""
Azure platform context — service naming, infrastructure details, and
tech-stack-specific message flavour for the simulation.

Services are C# ASP.NET App Services deployed to Azure.
Infrastructure is managed with Terraform via Azure DevOps pipelines.
Services communicate over APIM (API Management) or Azure Event Hubs.
Networking is through VNet / subnets / Front Door / private endpoints.
"""
import random

# Azure infrastructure resource types that appear in chat / events
AZURE_INFRA = [
    "APIM", "Front Door", "App Service Plan", "Event Hub", "Service Bus",
    "Key Vault", "Azure DevOps pipeline", "Terraform state", "VNet peering",
    "Private Endpoint", "Azure Monitor", "Application Insights", "Azure SQL",
    "Cosmos DB", "Azure Cache for Redis", "Storage Account", "Azure DNS",
    "NSG rule", "Subnet", "Managed Identity", "App Registration",
    "Azure Container Registry", "Azure Firewall", "Load Balancer", "Traffic Manager",
]

AZURE_DEVOPS_TERMS = [
    "the ADO pipeline", "the release gate", "the YAML pipeline",
    "the build agent", "the artifact feed", "the environment approval",
    "the variable group in ADO", "the service connection",
    "the ADO repo", "the pull request policy", "the branch policy",
    "the work item", "the deployment slot swap",
]

TERRAFORM_TERMS = [
    "the Terraform plan", "the TF state", "the terraform apply",
    "the state lock", "the Terraform module", "the remote backend",
    "the tfvars file", "the terraform workspace", "the resource group config",
    "the Terraform provider version", "the output variables",
]

CSHARP_TERMS = [
    "the middleware pipeline", "the DI container", "the hosted service",
    "the minimal API", "the controller", "the HttpClient factory",
    "the background worker", "Entity Framework migration",
    "the Polly retry policy", "the MediatR handler", "the FluentValidation rule",
    "the Serilog sink", "the health check endpoint", "the xUnit test",
    "the integration test with TestServer", "the NuGet package",
    "the .csproj dependencies", "the nullable reference warning",
    "the async void method someone wrote", "the LINQ query that became SQL",
    "the ConfigureAwait(false) someone removed", "the CancellationToken nobody passed",
]

# Azure/DevOps/C# flavoured blockers for standup
AZURE_BLOCKERS = [
    "waiting on APIM policy to be approved in ADO",
    "the Terraform state is locked by a previous failed apply",
    "the Event Hub consumer group was deleted in staging",
    "the ADO pipeline is failing on the Terraform plan step",
    "the App Service deployment slot is stuck in a swap",
    "the Key Vault access policy isn't propagated yet",
    "can't merge — the branch policy requires 2 reviewers and one is on PTO",
    "the private endpoint for the SQL database isn't resolving in the VNet",
    "the Managed Identity doesn't have the right role on the storage account",
    "Entity Framework migration failed in staging. rolling back.",
    "the APIM rate limit is hitting our integration tests",
    "the ADO service connection credentials expired",
    "Front Door health probe is failing because the endpoint isn't behind APIM yet",
    "the Terraform module for the VNet subnet has a breaking change in v2",
    "the App Registration secret expired in non-prod",
    "the build agent is out of disk space",
    "the NuGet private feed is returning 401s",
    "waiting on the NSG rule to be reviewed by the cloud governance team",
    "the staging slot has a different app setting than prod — caused data issues",
    "the ADO environment approval has been sitting for 3 days",
    "the YAML pipeline needs a new variable group but I don't have access to create it",
    "the cosmos DB throughput isn't provisioned correctly via Terraform yet",
    "the Application Insights instrumentation key got rotated and nothing was updated",
    "the dev VNet peering to the shared services VNet is broken",
    "waiting on the enterprise architect to approve the new subnet CIDR",
]

# Azure/C# flavoured dev chat messages
AZURE_DEV_MESSAGES = [
    "the APIM policy for {service} is blocking the request. need to debug the XML",
    "EF migration for {service} is going to need a manual script in prod",
    "anyone know why the App Service for {service} is scaling to zero under load?",
    "the Event Hub partition key strategy for {service} is wrong — we're getting hot partitions",
    "the Polly retry policy in {service} is retrying on 400s. that's bad.",
    "the Terraform plan for the {service} module has 47 changes. reviewing.",
    "the ADO pipeline for {service} passed. deploying to staging now.",
    "the deployment slot swap for {service} failed. investigating.",
    "the {service} App Service is hitting OOM. need to bump the App Service Plan SKU",
    "why does {service} have 3 different app settings files? which one is prod?",
    "the Managed Identity for {service} is missing the Storage Blob Data Reader role",
    "Application Insights for {service} is showing 200 exceptions a minute",
    "the Event Hub consumer for {service} is 6 hours behind on messages",
    "the Front Door WAF policy is blocking legitimate requests to {service}",
    "I need to add a new private endpoint for {service} but it requires a VNet change",
    "the {service} Entity Framework query is doing a table scan. adding an index via migration",
    "the DI registration for {service} has a scoped service in a singleton. bad.",
    "the NuGet restore is pulling an old version of the shared library. updating the lock file",
    "the background worker in {service} is not stopping gracefully on App Service restart",
    "I updated the Terraform for {service}'s APIM subscription. needs a plan review.",
    "the YAML pipeline for {service} is using a deprecated task version. updating.",
    "the CancellationToken isn't being passed through the {service} handler chain",
    "FluentValidation for {service} is returning a 500 instead of 400. middleware issue.",
    "anyone free to review the Terraform PR for the {service} resource group?",
    "the {service} service bus dead-letter queue has 4000 messages. investigating.",
    "added structured logging to {service} with Serilog. it now outputs JSON to App Insights.",
    "the async void in {service}'s startup code is swallowing exceptions silently",
    "the {service} health check is hitting the database on every probe. that's... a lot",
    "I'm running `terraform apply` on the VNet changes. everyone hold",
    "the App Registration for {service} has too many owners and no service principal",
]

# Azure incident messages
AZURE_INCIDENT_MESSAGES = [
    "{service} App Service is throwing 500s. checking Application Insights.",
    "the ADO deployment to {service} just went wrong. initiating slot swap rollback.",
    "APIM is returning 503 for all requests to {service}. backend pool unhealthy.",
    "the Event Hub for {service} is throttling. consumer group is behind.",
    "Front Door health probe failing for {service}. origin is down.",
    "{service} EF migration ran in prod and it dropped a column. not great.",
    "the Terraform apply for {service} infrastructure failed mid-way. state is dirty.",
    "Key Vault access revoked for {service} Managed Identity. service is broken.",
    "the App Service Plan for {service} is at 100% CPU. scaling out now.",
    "{service} is fine but it's taking down everything behind the VNet peering",
    "the Service Bus namespace for {service} hit its message limit",
    "Cosmos DB for {service} is throttling — RUs provisioned are too low",
    "{service} deployment slot failed to warm up. slot swap aborted.",
    "the NSG rule change blocked {service} from reaching the shared SQL server",
    "ADO pipeline for {service} is stuck. build agent is unresponsive.",
    "{service} private endpoint DNS isn't resolving inside the VNet",
    "the app setting for {service}'s connection string is wrong in prod",
    "{service} Managed Identity certificate expired. all outbound calls failing.",
    "the {service} background worker crashed and isn't restarting — App Service webjob issue",
    "alert: {service} Application Insights showing error rate > 10% for 5 mins",
]

# Architecture-specific Azure messages
AZURE_ARCHITECTURE_MESSAGES = [
    "should {service} talk to the other service via APIM or directly through the VNet?",
    "we need to decide: Event Hub or Service Bus for the {service} events",
    "the current {service} design puts secrets in app settings. should be Key Vault refs.",
    "I'm concerned we have too many App Service Plans. consolidation?",
    "should {service} be its own App Registration or share with the gateway?",
    "the Terraform module structure doesn't match our resource group layout",
    "we need a proper APIM versioning strategy before the next release",
    "the VNet topology doesn't support the new {service} private endpoint without a subnet change",
    "the Front Door WAF policy needs updating — it's blocking {service} traffic",
    "are we doing blue-green deploys or canary for {service}? the pipeline doesn't reflect a decision",
    "the shared library versioning is getting out of hand — Nuget feed has 30 versions",
    "the Managed Identity approach for {service} is cleaner but requires an ADO service connection update",
    "every service has its own Azure Monitor alert rules. we need a shared alert policy.",
    "the Terraform state is split across too many backends. hard to see the whole picture",
    "should the {service} Event Hub consumer be in the same App Service or a separate Function App?",
    "we're using both HTTP and Service Bus to do the same thing in different services",
    "the Application Insights sampling rate is set to 100%. costs will be high at scale.",
    "does the enterprise architecture team know we're adding a new subnet?",
    "I want to propose moving {service} to a Consumption-based App Service Plan",
    "the APIM policy for auth is copy-pasted across 6 APIs. it should be a policy fragment",
]


def azure_flavoured_blocker() -> str:
    return random.choice(AZURE_BLOCKERS)


def azure_flavoured_dev_message(service: str) -> str:
    return random.choice(AZURE_DEV_MESSAGES).replace("{service}", service)


def azure_flavoured_incident_message(service: str) -> str:
    return random.choice(AZURE_INCIDENT_MESSAGES).replace("{service}", service)


def azure_flavoured_architecture_message(service: str) -> str:
    return random.choice(AZURE_ARCHITECTURE_MESSAGES).replace("{service}", service)


def random_azure_resource() -> str:
    return random.choice(AZURE_INFRA)


def random_devops_term() -> str:
    return random.choice(AZURE_DEVOPS_TERMS)


def random_terraform_term() -> str:
    return random.choice(TERRAFORM_TERMS)


def random_csharp_term() -> str:
    return random.choice(CSHARP_TERMS)
