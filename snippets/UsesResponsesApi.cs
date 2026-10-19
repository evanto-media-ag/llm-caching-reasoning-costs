// Excerpt from Evanto.ChatClients: Factories/EvChatClientFactory.cs
// Provider "OpenAI" alone is not enough: every OpenAI-compatible gateway (Cortecs, EU Router,
// Requesty, Scaleway, ...) is filed under it, and those only speak Chat Completions.
internal static Boolean UsesResponsesApi(EvChatClientSettings settings)
    => String.Equals(settings.ProviderName, "OpenAI", StringComparison.OrdinalIgnoreCase)
       && Uri.TryCreate(settings.Endpoint, UriKind.Absolute, out var endpoint)
       && String.Equals(endpoint.Host, OPENAI_API_HOST, StringComparison.OrdinalIgnoreCase);
