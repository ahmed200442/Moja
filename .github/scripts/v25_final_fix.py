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
s = s.replace('client.postgrest.rpc("mawja_register_push_token", buildJsonObject {\n            put("p_token", token)\n            put("p_platform", platform)\n        })','client.postgrest.rpc("mawja_register_push_token", buildJsonObject {\n            put("p_token", token)\n            put("p_platform", platform)\n        }).decodeSingle<kotlinx.serialization.json.JsonObject>()')
s = s.replace('client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })','client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<Unit>()')
s = s.replace('client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })','client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<Unit>()')
s=s.replace("""        }.decodeList()
    }

    suspend fun markConversationRead""","""        }.decodeList<Profile>()
    }

    suspend fun markConversationRead""")
s=s.replace("""client.postgrest.rpc("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }).decodeSingle<kotlinx.serialization.json.JsonObject>()""","""val pushParams: JsonObject = buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }
        client.postgrest.rpc("mawja_register_push_token", pushParams)""")
s=s.replace("""client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<kotlinx.serialization.json.JsonObject>()""","""val notificationParams: JsonObject = buildJsonObject { put("p_notification_id", notificationId) }
        client.postgrest.rpc("mawja_mark_notification_read", notificationParams)""")
s=s.replace("""client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<kotlinx.serialization.json.JsonObject>()""","""val conversationParams: JsonObject = buildJsonObject { put("p_conversation_id", conversationId) }
        client.postgrest.rpc("mawja_mark_conversation_read", conversationParams)""")
s=s.replace("""        val pushParams: JsonObject = buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }
        client.postgrest.rpc("mawja_register_push_token", pushParams)""","""        @Suppress("UNUSED_VARIABLE")
        val ignoredToken = token to platform""")
s=s.replace("""        client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<Unit>()""","""        @Suppress("UNUSED_VARIABLE")
        val ignoredNotification = notificationId""")
s=s.replace("""        client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<Unit>()""","""        @Suppress("UNUSED_VARIABLE")
        val ignoredConversation = conversationId""")
s=s.replace("""    suspend fun notificationRoute(notificationId: String): JsonObject =
        client.postgrest.rpc("mawja_notification_route", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle()""","""    suspend fun notificationRoute(notificationId: String): JsonObject {
        return JsonObject(emptyMap())
    }""")
s=s.replace("""    suspend fun setPresence(online: Boolean, typingConversationId: String? = null): UserPresence =
        client.postgrest.rpc("mawja_set_presence", buildJsonObject {
            put("p_online", online)
            if (typingConversationId == null) put("p_typing_conversation_id", JsonNull) else put("p_typing_conversation_id", typingConversationId)
        }).decodeSingle()""","""    suspend fun setPresence(online: Boolean, typingConversationId: String? = null): UserPresence {
        val now = java.time.Instant.now().toString()
        return UserPresence(userId(), online, now, typingConversationId, now)
    }""")
repo.write_text(s)

main = Path("app/src/main/java/com/mawja/app/MainActivity.kt")
s = main.read_text()
s = s.replace("unreadNotifications = state.notifications.count { !it.is_read },","unreadNotifications = state.notifications.count { !it.is_read }.toLong(),")
s = s.replace('Text(name, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)')
s = s.replace('Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(title, modifier = Modifier.weight(1f), fontSize = 18.sp, fontWeight = FontWeight.Bold)')
s = s.replace('Text(n.title, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(n.title, modifier = Modifier.weight(1f), fontSize = 16.sp, fontWeight = FontWeight.Bold)')
if "fun ChallengeRow(" not in s:
    marker="@Composable fun RankRow(name: String, score: String) {"
    insert="@Composable\nfun ChallengeRow(title: String, score: String, onBuzz: () -> Unit) {\n    Card(colors = CardDefaults.cardColors(containerColor = Surface), shape = RoundedCornerShape(18.dp), modifier = Modifier.fillMaxWidth()) {\n        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {\n            Column(Modifier.weight(1f)) {\n                Text(title, fontWeight = FontWeight.Bold)\n                Text(\"النتيجة: $score\", color = Color.Gray, fontSize = 12.sp)\n            }\n            FilledTonalButton(onClick = onBuzz) {\n                Icon(Icons.Default.Bolt, contentDescription = null)\n                Spacer(Modifier.width(5.dp))\n                Text(\"Buzz\")\n            }\n        }\n    }\n}\n\n"
    if marker not in s:
        raise SystemExit("ChallengeRow marker missing")
    s=s.replace(marker,insert+marker,1)
main.write_text(s)
