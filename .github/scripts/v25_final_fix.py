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

# Avoid nested lambda type inference by materializing RPC parameters first.
s=s.replace(
'''    suspend fun registerPushToken(token: String, platform: String = "android") {
        client.postgrest.rpc<JsonObject>("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        })
    }''',
'''    suspend fun registerPushToken(token: String, platform: String = "android") {
        val params = buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }
        client.postgrest.rpc("mawja_register_push_token", params)
    }'''
)
s=s.replace(
'''    suspend fun markNotificationRead(notificationId: String) {
        client.postgrest.rpc<JsonObject>("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })
    }''',
'''    suspend fun markNotificationRead(notificationId: String) {
        val params = buildJsonObject { put("p_notification_id", notificationId) }
        client.postgrest.rpc("mawja_mark_notification_read", params)
    }'''
)
s=s.replace(
'''    suspend fun markConversationRead(conversationId: String) {
        client.postgrest.rpc<JsonObject>("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })
    }''',
'''    suspend fun markConversationRead(conversationId: String) {
        val params = buildJsonObject { put("p_conversation_id", conversationId) }
        client.postgrest.rpc("mawja_mark_conversation_read", params)
    }'''
)
s=s.replace(
'''return client.from("profiles").select {
        filter { isIn("id", ids) }
    }.decodeList()''',
'''return client.from("profiles").select {
        filter { isIn("id", ids) }
    }.decodeList<Profile>()'''
)
p.write_text(s)
