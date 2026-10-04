from pathlib import Path

p = Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s = p.read_text()

s = s.replace(
    "import io.github.jan.supabase.auth.providers.builtin.Email",
    "import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email",
)
s = s.replace("import io.github.jan.supabase.functions.invoke\n", "")
s = s.replace(
    "import io.github.jan.supabase.postgrest.from",
    "import io.github.jan.supabase.postgrest.from\nimport io.github.jan.supabase.postgrest.postgrest",
)
s = s.replace(
    "import io.github.jan.supabase.postgrest.query.filter.FilterOperation",
    "import io.github.jan.supabase.functions.functions\nimport io.github.jan.supabase.postgrest.query.filter.FilterOperation",
)
s = s.replace(
    "import kotlinx.serialization.json.JsonObject",
    "import io.ktor.client.call.body\nimport kotlinx.serialization.json.JsonObject",
)

# Typed serializable RPC parameters.
if "import kotlinx.serialization.Serializable" not in s:
    s = s.replace(
        "import kotlinx.serialization.json.JsonObject",
        "import kotlinx.serialization.Serializable\nimport kotlinx.serialization.json.JsonObject",
    )

if "data class RegisterPushTokenParams" not in s:
    s = s.replace(
        "class MawjaRepository {",
        """@Serializable
data class RegisterPushTokenParams(val p_token: String, val p_platform: String)

@Serializable
data class NotificationReadParams(val p_notification_id: String)

@Serializable
data class ConversationReadParams(val p_conversation_id: String)

@Serializable
data class PresenceParams(val p_online: Boolean, val p_typing_conversation_id: String?)

class MawjaRepository {""",
        1,
    )

start = s.index("    suspend fun registerPushToken")
end = s.index("    suspend fun markNotificationRead", start)
s = s[:start] + """    suspend fun registerPushToken(token: String, platform: String = "android") {
        client.postgrest.rpc("mawja_register_push_token", RegisterPushTokenParams(token, platform))
    }

""" + s[end:]

start = s.index("    suspend fun markNotificationRead")
end = s.index("    suspend fun notificationRoute", start)
s = s[:start] + """    suspend fun markNotificationRead(notificationId: String) {
        client.postgrest.rpc("mawja_mark_notification_read", NotificationReadParams(notificationId))
    }

""" + s[end:]

start = s.index("    suspend fun profilesByIds")
end = s.index("    suspend fun markConversationRead", start)
s = s[:start] + """    suspend fun profilesByIds(ids: List<String>): List<Profile> {
        if (ids.isEmpty()) return emptyList()
        return client.from("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList<Profile>()
    }

""" + s[end:]

start = s.index("    suspend fun markConversationRead")
end = s.index("    suspend fun setPresence", start)
s = s[:start] + """    suspend fun markConversationRead(conversationId: String) {
        client.postgrest.rpc("mawja_mark_conversation_read", ConversationReadParams(conversationId))
    }

""" + s[end:]

start = s.index("    suspend fun inbox")
end = s.index("    suspend fun profilesByIds", start)
s = s[:start] + """    suspend fun inbox(): List<InboxRow> = client.from<InboxRow>("mawja_inbox").select {
        filter { eq("user_id", userId()) }
    }.decodeList<InboxRow>().sortedByDescending { it.last_message_at ?: it.updated_at }

""" + s[end:]

start = s.index("    suspend fun profilesByIds")
end = s.index("    suspend fun markConversationRead", start)
s = s[:start] + """    suspend fun profilesByIds(ids: List<String>): List<Profile> {
        if (ids.isEmpty()) return emptyList()
        return client.from<Profile>("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList<Profile>()
    }

""" + s[end:]

start = s.index("    suspend fun setPresence")
end = s.index("    fun presenceFlow", start)
s = s[:start] + """    suspend fun setPresence(online: Boolean, typingConversationId: String? = null): UserPresence =
        client.postgrest.rpc(
            "mawja_set_presence",
            PresenceParams(online, typingConversationId)
        ).decodeSingle<UserPresence>()

""" + s[end:]

p.write_text(s)
