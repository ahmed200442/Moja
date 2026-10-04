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
 "notifications":"Notification", "inbox":"InboxRow",
 "profilesByIds":"Profile"
}
for name, typ in types.items():
    s = re.sub(r"(suspend fun "+re.escape(name)+r"([^\n]*)[^\n]*?)\.decodeList\(\)", r"\1.decodeList<"+typ+">()", s)
for name, typ in {"profile":"Profile","wallet":"Wallet","notificationRoute":"JsonObject","setPresence":"UserPresence"}.items():
    s = re.sub(r"(suspend fun "+re.escape(name)+r"([^\n]*)[^\n]*?)\.decodeSingle\(\)", r"\1.decodeSingle<"+typ+">()", s)

s = s.replace('client.postgrest.rpc("mawja_register_push_token", buildJsonObject {\n            put("p_token", token)\n            put("p_platform", platform)\n        })','client.postgrest.rpc("mawja_register_push_token", buildJsonObject {\n            put("p_token", token)\n            put("p_platform", platform)\n        }).decodeSingle<Unit>()')
s = s.replace('client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })','client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<Unit>()')
s = s.replace('client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })','client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<Unit>()')
repo.write_text(s)

main = Path("app/src/main/java/com/mawja/app/MainActivity.kt")
s = main.read_text()
s = s.replace("unreadNotifications = state.notifications.count { !it.is_read },","unreadNotifications = state.notifications.count { !it.is_read }.toLong(),")
s = s.replace('Text(name, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)')
s = s.replace('Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(title, modifier = Modifier.weight(1f), fontSize = 18.sp, fontWeight = FontWeight.Bold)')
s = s.replace('Text(n.title, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(n.title, modifier = Modifier.weight(1f), fontSize = 16.sp, fontWeight = FontWeight.Bold)')
main.write_text(s)
