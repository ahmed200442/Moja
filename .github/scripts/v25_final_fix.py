from pathlib import Path

# Final compatibility fixes for V25 with Kotlin 2.2 / Supabase-kt 3.5.
p = Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s = p.read_text()

# Supabase auth/functions/postgrest extension imports.
s = s.replace("import io.github.jan.supabase.auth.providers.Email",
              "import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email")
s = s.replace("import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.auth\n",
              "import io.github.jan.supabase.auth.auth\n")
s = s.replace("import io.github.jan.supabase.functions.invoke\n", "")
if "import io.github.jan.supabase.functions.functions" not in s:
    s = s.replace("import io.github.jan.supabase.postgrest.from",
                  "import io.github.jan.supabase.functions.functions\nimport io.github.jan.supabase.postgrest.from")
if "import io.github.jan.supabase.postgrest.postgrest" not in s:
    s = s.replace("import io.github.jan.supabase.postgrest.from",
                  "import io.github.jan.supabase.postgrest.from\nimport io.github.jan.supabase.postgrest.postgrest")
if "import io.ktor.client.call.body" not in s:
    s = s.replace("import kotlinx.serialization.json.JsonObject",
                  "import io.ktor.client.call.body\nimport kotlinx.serialization.json.JsonObject")

# Explicit result types where Kotlin 2.2 cannot infer the RPC generic.
s = s.replace('''client.postgrest.rpc<Unit>("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        })''',
              '''client.postgrest.rpc<Unit>("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }).decodeSingle<Unit>()''')
s = s.replace('''client.postgrest.rpc<Unit>("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })''',
              '''client.postgrest.rpc<Unit>("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<Unit>()''')
s = s.replace('''client.postgrest.rpc<Unit>("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })''',
              '''client.postgrest.rpc<Unit>("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<Unit>()''')

# Explicit list type for profile query.
s = s.replace('''return client.from("profiles").select {
        filter { isIn("id", ids) }
    }.decodeList()''',
              '''return client.from("profiles").select {
        filter { isIn("id", ids) }
    }.decodeList<Profile>()''')

# Explicit Unit for profile update if present in the source.
s = s.replace('client.postgrest.from("profiles").update(buildJsonObject { put("name", name) }) { filter { eq("id", id) } }',
              'client.postgrest.from("profiles").update(buildJsonObject { put("name", name) }) { filter { eq("id", id) } }.decodeSingle<Unit>()')

# Replace the affected repository methods as complete blocks for deterministic Kotlin 2.2 inference.
start = s.index("    suspend fun registerPushToken")
end = s.index("    suspend fun markNotificationRead", start)
s = s[:start] + """    suspend fun registerPushToken(token: String, platform: String = "android") {
        client.postgrest.rpc("mawja_register_push_token", buildJsonObject {
            put("p_token", token)
            put("p_platform", platform)
        }).decodeSingle<Unit>()
    }

""" + s[end:]

start = s.index("    suspend fun markNotificationRead")
end = s.index("    suspend fun notificationRoute", start)
s = s[:start] + """    suspend fun markNotificationRead(notificationId: String) {
        client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject {
            put("p_notification_id", notificationId)
        }).decodeSingle<Unit>()
    }

""" + s[end:]

start = s.index("    suspend fun profilesByIds")
end = s.index("    suspend fun markConversationRead", start)
s = s[:start] + """    suspend fun profilesByIds(ids: List<String>): List<Profile> {
        if (ids.isEmpty()) return emptyList<Profile>()
        return client.from("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList<Profile>()
    }

""" + s[end:]

start = s.index("    suspend fun markConversationRead")
end = s.index("    suspend fun setPresence", start)
s = s[:start] + """    suspend fun markConversationRead(conversationId: String) {
        client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject {
            put("p_conversation_id", conversationId)
        }).decodeSingle<Unit>()
    }

""" + s[end:]

p.write_text(s)

# MainActivity UI/type fixes.
p = Path("app/src/main/java/com/mawja/app/MainActivity.kt")
s = p.read_text()
s = s.replace("unreadNotifications = state.notifications.count { !it.is_read },",
              "unreadNotifications = state.notifications.count { !it.is_read }.toLong(),")
s = s.replace('Text(name, fontWeight = FontWeight.Bold, Modifier.weight(1f))',
              'Text(name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)')
s = s.replace('Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, Modifier.weight(1f))',
              'Text(title, modifier = Modifier.weight(1f), fontSize = 18.sp, fontWeight = FontWeight.Bold)')
s = s.replace('Text(n.title, fontWeight = FontWeight.Bold, Modifier.weight(1f))',
              'Text(n.title, modifier = Modifier.weight(1f), fontSize = 16.sp, fontWeight = FontWeight.Bold)')
if "fun ChallengeRow(" not in s:
    marker = "@Composable fun RankRow(name: String, score: String) {"
    insert = '''@Composable
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
    if marker not in s:
        raise SystemExit("ChallengeRow marker missing")
    s = s.replace(marker, insert + marker, 1)
p.write_text(s)
