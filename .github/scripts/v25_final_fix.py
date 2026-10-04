from pathlib import Path
import re

repo = Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s = repo.read_text()
if not s.startswith("@file:OptIn"):
    s = "@file:OptIn(kotlinx.serialization.ExperimentalSerializationApi::class)\n" + s
s = s.replace("import io.github.jan.supabase.auth.providers.Email", "import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email")
s = s.replace("import io.github.jan.supabase.functions.invoke", "import io.github.jan.supabase.functions.functions")
if "import io.github.jan.supabase.postgrest.postgrest" not in s:
    s = s.replace("import io.github.jan.supabase.postgrest.from", "import io.github.jan.supabase.postgrest.from\nimport io.github.jan.supabase.postgrest.postgrest")
if "import io.ktor.client.call.body" not in s:
    s = s.replace("import kotlinx.serialization.json.JsonObject", "import io.ktor.client.call.body\nimport kotlinx.serialization.json.JsonObject")

types = {
 "profile":"Profile", "wallet":"Wallet", "featuredWaves":"Wave",
 "leaderboard":"LeaderboardRow", "searchProfiles":"Profile",
 "friendships":"Friendship", "challenges":"Challenge",
 "notifications":"Notification", "inbox":"InboxRow"
}
for name, typ in types.items():
    s = re.sub(r"(suspend fun "+re.escape(name)+r"[^\n]*?\.decodeList)\(\)", r"\1<"+typ+">()", s, count=1)

s = s.replace('''.decodeList().sortedByDescending { it.created_at }''','''.decodeList<Notification>().sortedByDescending { it.created_at }''')
s = s.replace('''.decodeList().sortedByDescending { it.last_message_at ?: it.updated_at }''','''.decodeList<InboxRow>().sortedByDescending { it.last_message_at ?: it.updated_at }''')
s = s.replace('''return client.from("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList()''','''return client.from("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList<Profile>()''')

s = s.replace('client.postgrest.rpc("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        })','client.postgrest.rpc("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }).decodeSingle<Unit>()')
s = s.replace('client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })','client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<Unit>()')
s = s.replace('client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })','client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<Unit>()')
repo.write_text(s)

main = Path("app/src/main/java/com/mawja/app/MainActivity.kt")
s = main.read_text()
s = s.replace("unreadNotifications = state.notifications.count { !it.is_read },","unreadNotifications = state.notifications.count { !it.is_read }.toLong(),")
main.write_text(s)
