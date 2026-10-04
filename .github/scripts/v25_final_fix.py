from pathlib import Path

p = Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s = p.read_text()

s = s.replace(
    "import io.github.jan.supabase.auth.providers.builtin.Email",
    "import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email",
)
s = s.replace("import io.github.jan.supabase.functions.invoke\n", "")
s = s.replace(
    "import io.github.jan.supabase.postgrest.from
import io.github.jan.supabase.postgrest.query.Columns",
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
        val params: JsonObject = buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }
        client.postgrest.rpc("mawja_register_push_token", params)
    }

""" + s[end:]

start = s.index("    suspend fun markNotificationRead")
end = s.index("    suspend fun notificationRoute", start)
s = s[:start] + """    suspend fun markNotificationRead(notificationId: String) {
        val params: JsonObject = buildJsonObject { put("p_notification_id", notificationId) }
        client.postgrest.rpc("mawja_mark_notification_read", params)
    }

""" + s[end:]

start = s.index("    suspend fun inbox")
end = s.index("    suspend fun profilesByIds", start)
s = s[:start] + """    suspend fun inbox(): List<InboxRow> =
        client.from("mawja_inbox").select(columns = Columns.list("user_id", "conversation_id", "peer_id", "created_at", "updated_at", "last_read_at", "unread_count", "last_message", "last_message_at")).decodeList<InboxRow>()
            .filter { it.user_id == userId() }
            .sortedByDescending { it.last_message_at ?: it.updated_at }

""" + s[end:]

start = s.index("    suspend fun profilesByIds")
end = s.index("    suspend fun markConversationRead", start)
s = s[:start] + """    suspend fun profilesByIds(ids: List<String>): List<Profile> {
        if (ids.isEmpty()) return emptyList()
        return client.from("profiles").select().decodeList<Profile>().filter { it.id in ids }
    }

""" + s[end:]

start = s.index("    suspend fun markConversationRead")
end = s.index("    suspend fun setPresence", start)
s = s[:start] + """    suspend fun markConversationRead(conversationId: String) {
        val params: JsonObject = buildJsonObject { put("p_conversation_id", conversationId) }
        client.postgrest.rpc("mawja_mark_conversation_read", params)
    }

""" + s[end:]

start = s.index("    suspend fun setPresence")
end = s.index("    fun presenceFlow", start)
s = s[:start] + """    suspend fun setPresence(online: Boolean, typingConversationId: String? = null): UserPresence {
        val params: JsonObject = buildJsonObject {
            put("p_online", online)
            if (typingConversationId == null) put("p_typing_conversation_id", JsonNull)
            else put("p_typing_conversation_id", typingConversationId)
        }
        return client.postgrest.rpc("mawja_set_presence", params).decodeSingle<UserPresence>()
    }

""" + s[end:]

p.write_text(s)
