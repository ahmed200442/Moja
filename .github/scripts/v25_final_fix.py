from pathlib import Path

def replace_between(text, start_marker, end_marker, replacement):
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[:start] + replacement + text[end:]

# Repository fixes.
p = Path("app/src/main/java/com/mawja/app/data/MawjaRepository.kt")
s = p.read_text()

s = s.replace(
    "import io.github.jan.supabase.auth.providers.Email",
    "import io.github.jan.supabase.auth.auth\nimport io.github.jan.supabase.auth.providers.builtin.Email"
)
s = s.replace(
    "import io.github.jan.supabase.functions.invoke\n",
    ""
)
if "import io.github.jan.supabase.functions.functions" not in s:
    s = s.replace(
        "import io.github.jan.supabase.postgrest.from",
        "import io.github.jan.supabase.functions.functions\nimport io.github.jan.supabase.postgrest.from"
    )
if "import io.github.jan.supabase.postgrest.postgrest" not in s:
    s = s.replace(
        "import io.github.jan.supabase.postgrest.from",
        "import io.github.jan.supabase.postgrest.from\nimport io.github.jan.supabase.postgrest.postgrest"
    )
if "import io.ktor.client.call.body" not in s:
    s = s.replace(
        "import kotlinx.serialization.json.JsonObject",
        "import io.ktor.client.call.body\nimport kotlinx.serialization.json.JsonObject"
    )

s = replace_between(
    s,
    "    suspend fun registerPushToken",
    "    suspend fun markNotificationRead",
    '''    suspend fun registerPushToken(token: String, platform: String = "android") {
        val _: Any = client.postgrest.rpc(
            function = "mawja_register_push_token",
            parameters = buildJsonObject {
                put("p_token", token)
                put("p_platform", platform)
            }
        )
    }

'''
)

s = replace_between(
    s,
    "    suspend fun markNotificationRead",
    "    suspend fun notificationRoute",
    '''    suspend fun markNotificationRead(notificationId: String) {
        val _: Any = client.postgrest.rpc(
            function = "mawja_mark_notification_read",
            parameters = buildJsonObject {
                put("p_notification_id", notificationId)
            }
        )
    }

'''
)

s = replace_between(
    s,
    "    suspend fun profilesByIds",
    "    suspend fun markConversationRead",
    '''    suspend fun profilesByIds(ids: List<String>): List<Profile> {
        if (ids.isEmpty()) return emptyList<Profile>()
        val profiles: List<Profile> = client.from("profiles").select {
            filter { isIn("id", ids) }
        }.decodeList<Profile>()
        return profiles
    }

'''
)

s = replace_between(
    s,
    "    suspend fun markConversationRead",
    "    suspend fun setPresence",
    '''    suspend fun markConversationRead(conversationId: String) {
        val _: Any = client.postgrest.rpc(
            function = "mawja_mark_conversation_read",
            parameters = buildJsonObject {
                put("p_conversation_id", conversationId)
            }
        )
    }

'''
)

p.write_text(s)

# MainActivity compatibility fixes.
p = Path("app/src/main/java/com/mawja/app/MainActivity.kt")
s = p.read_text()
s = s.replace(
    "unreadNotifications = state.notifications.count { !it.is_read },",
    "unreadNotifications = state.notifications.count { !it.is_read }.toLong(),"
)
s = s.replace(
    'Text(name, fontWeight = FontWeight.Bold, Modifier.weight(1f))',
    'Text(name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)'
)
s = s.replace(
    'Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, Modifier.weight(1f))',
    'Text(title, modifier = Modifier.weight(1f), fontSize = 18.sp, fontWeight = FontWeight.Bold)'
)
s = s.replace(
    'Text(n.title, fontWeight = FontWeight.Bold, Modifier.weight(1f))',
    'Text(n.title, modifier = Modifier.weight(1f), fontSize = 16.sp, fontWeight = FontWeight.Bold)'
)

if "fun ChallengeRow(" not in s:
    marker = "@Composable fun RankRow(name: String, score: String) {"
    insert = '''@Composable
fun ChallengeRow(title: String, score: String, onBuzz: () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Surface),
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
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
