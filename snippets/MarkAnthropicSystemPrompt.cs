// Excerpt (shortened) from Evanto.ChatClients: Extensions/EvChatClientExtensions.cs
// The top-level marker alone caches only up to the last block; a new turn never hits.
// So the turn-stable system prompt moves to the front and gets its own breakpoint.
var cacheControl = new AnthropicMessages.CacheControlEphemeral { Ttl = cacheTtl };
var marked       = messages.ToList();

if (options?.Instructions is { } instructions)
{
    marked.Insert(0, new ChatMessage(ChatRole.System,
    [
        new TextContent(instructions)
        {
            RawRepresentation = new AnthropicMessages.TextBlockParam { Text = instructions, CacheControl = cacheControl }
        }
    ]));
}
