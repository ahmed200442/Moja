from pathlib import Path
import re

p = Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s = p.read_text()

# supabase-kt 3.x extension imports
if "import io.github.jan.supabase.auth.auth" not in s:
    s = s.replace(
        "import io.github.jan.supabase.auth.providers.builtin.Email",
        "import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email",
    )
if "import io.github.jan.supabase.postgrest.postgrest" not in s:
    s = s.replace(
        "import io.github.jan.supabase.postgrest.from",
        "import io.github.jan.supabase.postgrest.from\nimport io.github.jan.supabase.postgrest.postgrest",
    )
if "import io.github.jan.supabase.functions.functions" not in s:
    s = s.replace(
        "import io.github.jan.supabase.postgrest.query.filter.FilterOperation",
        "import io.github.jan.supabase.functions.functions\nimport io.github.jan.supabase.postgrest.query.filter.FilterOperation",
    )
s = s.replace("import io.github.jan.supabase.functions.invoke\n", "")
if "import io.ktor.client.call.body" not in s:
    s = s.replace(
        "import kotlinx.serialization.json.JsonObject",
        "import io.ktor.client.call.body\nimport kotlinx.serialization.json.JsonObject",
    )

# Make every side-effect RPC consume a typed response so Kotlin can infer T.
if "import kotlinx.serialization.json.JsonElement" not in s:
    s=s.replace("import kotlinx.serialization.json.JsonNull", "import kotlinx.serialization.json.JsonNull\nimport kotlinx.serialization.json.JsonElement")

start=s.index("    suspend fun registerPushToken")
end=s.index("    suspend fun markNotificationRead", start)
s=s[:start]+"""    suspend fun registerPushToken(token: String, platform: String = "android") {
        val params = buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }
        client.postgrest.rpc("mawja_register_push_token", params).decodeSingle<JsonElement>()
    }

"""+s[end:]

start=s.index("    suspend fun markNotificationRead")
end=s.index("    suspend fun notificationRoute", start)
s=s[:start]+"""    suspend fun markNotificationRead(notificationId: String) {
        val params = buildJsonObject { put("p_notification_id", notificationId) }
        client.postgrest.rpc("mawja_mark_notification_read", params).decodeSingle<JsonElement>()
    }

"""+s[end:]

start=s.index("    suspend fun profilesByIds")
end=s.index("    suspend fun markConversationRead", start)
s=s[:start]+"""    suspend fun profilesByIds(ids: List<String>): List<Profile> {
        if (ids.isEmpty()) return emptyList()
        return client.from("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList<Profile>()
    }

"""+s[end:]

start=s.index("    suspend fun markConversationRead")
end=s.index("    suspend fun setPresence", start)
s=s[:start]+"""    suspend fun markConversationRead(conversationId: String) {
        val params = buildJsonObject { put("p_conversation_id", conversationId) }
        client.postgrest.rpc("mawja_mark_conversation_read", params).decodeSingle<JsonElement>()
    }

"""+s[end:]
p.write_text(s)
