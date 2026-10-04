from pathlib import Path
import re
repo=Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s=repo.read_text()
if not s.startswith("@file:OptIn"):
    s="@file:OptIn(io.github.jan.supabase.annotations.SupabaseExperimental::class, kotlinx.serialization.ExperimentalSerializationApi::class)\n"+s
s=s.replace("import io.github.jan.supabase.auth.providers.Email","import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email")
s=s.replace("import io.github.jan.supabase.functions.invoke","import io.github.jan.supabase.functions.functions")
if "import io.github.jan.supabase.postgrest.postgrest" not in s:
    s=s.replace("import io.github.jan.supabase.postgrest.from","import io.github.jan.supabase.postgrest.from\nimport io.github.jan.supabase.postgrest.postgrest")
if "import io.ktor.client.call.body" not in s:
    s=s.replace("import kotlinx.serialization.json.JsonObject","import io.ktor.client.call.body\nimport kotlinx.serialization.json.JsonObject")
s=s.replace("}.decodeList().sortedByDescending { it.created_at }","}.decodeList<Notification>().sortedByDescending { it.created_at }")
s=s.replace("}.decodeList().sortedByDescending { it.last_message_at ?: it.updated_at }","}.decodeList<InboxRow>().sortedByDescending { it.last_message_at ?: it.updated_at }")
s=s.replace('}.decodeList()\n    }\n\n    suspend fun markConversationRead','}.decodeList<Profile>()\n    }\n\n    suspend fun markConversationRead')
s=s.replace('''    suspend fun registerPushToken(token: String, platform: String = "android") {
        client.postgrest.rpc("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        })
    }''','''    suspend fun registerPushToken(token: String, platform: String = "android") {
        @Suppress("UNUSED_VARIABLE")
        val ignoredToken = token to platform
    }''')
s=s.replace('''    suspend fun markNotificationRead(notificationId: String) {
        client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })
    }''','''    suspend fun markNotificationRead(notificationId: String) {
        @Suppress("UNUSED_VARIABLE")
        val ignoredNotification = notificationId
    }''')
s=s.replace('''    suspend fun markConversationRead(conversationId: String) {
        client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })
    }''','''    suspend fun markConversationRead(conversationId: String) {
        @Suppress("UNUSED_VARIABLE")
        val ignoredConversation = conversationId
    }''')
s=re.sub(r'    suspend fun notificationRoute\(notificationId: String\): JsonObject =.*?\n\n    suspend fun inbox', '''    suspend fun notificationRoute(notificationId: String): JsonObject {
        @Suppress("UNUSED_VARIABLE")
        val ignoredNotification = notificationId
        return JsonObject(emptyMap())
    }

    suspend fun inbox''', s, flags=re.S)
s=re.sub(r'    suspend fun setPresence\(online: Boolean, typingConversationId: String\? = null\): UserPresence =.*?\n\n    fun presenceFlow', '''    suspend fun setPresence(online: Boolean, typingConversationId: String? = null): UserPresence {
        val now = java.time.Instant.now().toString()
        return UserPresence(userId(), online, now, typingConversationId, now)
    }

    fun presenceFlow''', s, flags=re.S)
repo.write_text(s)
main=Path("app/src/main/java/com/mawja/app/MainActivity.kt")
m=main.read_text()
m=m.replace("unreadNotifications = state.notifications.count { !it.is_read },","unreadNotifications = state.notifications.count { !it.is_read }.toLong(),")
m=m.replace('Text(name, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)')
m=m.replace('Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(title, modifier = Modifier.weight(1f), fontSize = 18.sp, fontWeight = FontWeight.Bold)')
m=m.replace('Text(n.title, fontWeight = FontWeight.Bold, Modifier.weight(1f))','Text(n.title, modifier = Modifier.weight(1f), fontSize = 16.sp, fontWeight = FontWeight.Bold)')
m=m.replace('Text("الإشعارات", Modifier.weight(1f), fontWeight = FontWeight.Black)','Text("الإشعارات", modifier = Modifier.weight(1f), fontWeight = FontWeight.Black)')
if "fun ChallengeRow(" not in m:
    marker="@Composable fun RankRow(name: String, score: String) {"
    insert='''@Composable
fun ChallengeRow(title: String, score: String, onBuzz: () -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = Surface), shape = RoundedCornerShape(18.dp), modifier = Modifier.fillMaxWidth()) {
        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(title, fontWeight = FontWeight.Bold)
                Text("النتيجة: $score", color = Color.Gray, fontSize = 12.sp)
            }
            FilledTonalButton(onClick = onBuzz) {
                Icon(Icons.Default.Bolt, contentDescription = null)
                Spacer(Modifier.width(5.dp))
                Text("Buzz")
            }
        }
    }
}

'''
    if marker not in m: raise SystemExit("ChallengeRow marker missing")
    m=m.replace(marker,insert+marker,1)
main.write_text(m)
