// Excerpt from Evanto.ChatClients: Extensions/EvChatClientExtensions.cs
// One effort vocabulary for every provider; Anthropic gets its own mapping.
// None becomes low: current Claude models reject "none" (measured: HTTP 400).
private static String? ToAnthropicEffort(ReasoningEffort effort) => effort switch
{
    ReasoningEffort.None      => "low",
    ReasoningEffort.Low       => "low",
    ReasoningEffort.Medium    => "medium",
    ReasoningEffort.High      => "high",
    ReasoningEffort.ExtraHigh => "xhigh",
    _                         => null
};
