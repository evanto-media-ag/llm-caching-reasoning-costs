// Excerpt from CompanyWizard: lib/Evanto.CompanyWizard.Core/Services/TurnTokenUsage.cs
// Microsoft.Extensions.AI has a property for cache reads, but none for cache writes.
// The Anthropic adapter puts writes into AdditionalCounts; the key is set only when > 0.
public const String CacheCreationInputTokensKey = "CacheCreationInputTokens";

public TurnTokenUsage Add(UsageDetails? usage)
{
    var cacheWrite = usage.AdditionalCounts?.TryGetValue(CacheCreationInputTokensKey, out var written) == true ? written : 0L;

    return new TurnTokenUsage(
        Input      + (Int32) (usage.InputTokenCount       ?? 0),
        Output     + (Int32) (usage.OutputTokenCount      ?? 0),
        CacheRead  + (Int32) (usage.CachedInputTokenCount ?? 0),
        CacheWrite + (Int32) cacheWrite);
}
