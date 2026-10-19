// Excerpt (shortened) from CompanyWizard: lib/Evanto.CompanyWizard.Core/Services/ModelCostCalculator.cs
// One formula for every provider. A missing cache price falls back to the input price.
public static Decimal Calculate(ModelDefinition model, String? promptCacheTtl, TurnTokenUsage tokens)
{
    var billedInput = Math.Max(0, tokens.Input - tokens.CacheRead - tokens.CacheWrite);
    var readPrice   = model.CacheReadPricePer1M ?? model.InputPricePer1M;
    var writePrice  = (promptCacheTtl == OneHourTtl ? model.CacheWrite1hPricePer1M : model.CacheWritePricePer1M)
                      ?? model.InputPricePer1M;

    return (billedInput       * model.InputPricePer1M
          + tokens.CacheRead  * readPrice
          + tokens.CacheWrite * writePrice
          + tokens.Output     * model.OutputPricePer1M) / TokensPerMillion;
}
