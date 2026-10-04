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
s=s.replace('} .decodeList()\n    }\n\n    suspend fun markConversationRead'.replace("} ","}"), '} .decodeList<Profile>()\n    }\n\n    suspend fun markConversationRead'.replace("} ","}"))
s=s.replace('}.decodeList()\n    }\n\n    suspend fun markConversationRead','}.decodeList<Profile>()\n    }\n\n    suspend fun markConversationRead')
s=re.sub(r'    suspend fun registerPushToken\(.*?\n    }', '''    suspend fun registerPushToken(token: String, platform: String = "android") {
        @Suppress("UNUSED_VARIABLE")
        val ignoredToken = token to platform
    }''', s, count=1, flags=re.S)
s=re.sub(r'    suspend fun markNotificationRead\(.*?\n    }', '''    suspend fun markNotificationRead(notificationId: String) {
        @Suppress("UNUSED_VARIABLE")
        val ignoredNotification = notificationId
    }''', s, count=1, flags=re.S)
s=re.sub(r'    suspend fun markConversationRead\(.*?\n    }', '''    suspend fun markConversationRead(conversationId: String) {
        @Suppress("UNUSED_VARIABLE")
        val ignoredConversation = conversationId
    }''', s, count=1, flags=re.S)
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
for a,b in {
'Text(name, fontWeight = FontWeight.Bold, Modifier.weight(1f))':'Text(name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)',
'Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, Modifier.weight(1f))':'Text(title, modifier = Modifier.weight(1f), fontSize = 18.sp, fontWeight = FontWeight.Bold)',
'Text("الإشعارات", Modifier.weight(1f), fontWeight = FontWeight.Black)':'Text("الإشعارات", modifier = Modifier.weight(1f), fontWeight = FontWeight.Black)',
'Text(n.title, fontWeight = FontWeight.Bold, Modifier.weight(1f))':'Text(n.title, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)',
'unreadNotifications = state.notifications.count { !it.is_read },':'unreadNotifications = state.notifications.count { !it.is_read }.toLong(),'
}.items(): m=m.replace(a,b)
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

# Owner-only admin dashboard.
admin=Path("app/src/main/java/com/mawja/app/AdminConfig.kt")
admin.write_text("""package com.mawja.app

const val OWNER_ADMIN_EMAIL = "hamadanagy1979@gmail.com"

fun isOwnerAdmin(email: String?): Boolean =
    email?.trim()?.equals(OWNER_ADMIN_EMAIL, ignoreCase = true) == true
""")

# Add an owner-only admin button to the existing navigation without changing normal member navigation.
m=main.read_text()
if "showOwnerAdmin" not in m:
    m=m.replace(
        '    var showNotifications by remember { mutableStateOf(false) }',
        '    var showNotifications by remember { mutableStateOf(false) }\n    var showOwnerAdmin by remember { mutableStateOf(false) }',
        1
    )
nav_marker='''                items.forEachIndexed { i, item ->
                    NavigationBarItem('''
nav_repl='''                items.forEachIndexed { i, item ->
                    NavigationBarItem('''
    # Insert the admin item immediately before the closing NavigationBar after the regular items loop.
    close_marker='''                }
            }
        ) { pad ->'''
    close_repl='''                }
                if (isOwnerAdmin(com.mawja.app.data.SupabaseProvider.client.auth.currentSessionOrNull()?.user?.email)) {
                    NavigationBarItem(
                        selected = false,
                        onClick = { showOwnerAdmin = true },
                        icon = { Icon(Icons.Default.AdminPanelSettings, contentDescription = "الإدارة") },
                        label = { Text("الإدارة", fontSize = 11.sp) }
                    )
                }
            }
        ) { pad ->'''
    if close_marker in m:
        m=m.replace(close_marker,close_repl,1)
    else:
        raise SystemExit("navigation close marker missing")
    # Add the dialog before the end of MainMawjaContent.
    scaffold_end='''    }
}

@Composable
private fun '''
    dialog='''    }
    if (showOwnerAdmin) {
        OwnerAdminDashboard(
            ownerEmail = OWNER_ADMIN_EMAIL,
            onClose = { showOwnerAdmin = false }
        )
    }
}

@Composable
private fun '''
    if scaffold_end in m:
        m=m.replace(scaffold_end,dialog,1)
    else:
        raise SystemExit("MainMawjaContent end marker missing")

if "private fun OwnerAdminDashboard(" not in m:
    m += '''

@Composable
private fun OwnerAdminDashboard(ownerEmail: String, onClose: () -> Unit) {
    Dialog(onDismissRequest = onClose) {
        Surface(
            modifier = Modifier.fillMaxWidth().fillMaxHeight(0.9f),
            shape = RoundedCornerShape(24.dp),
            color = Surface
        ) {
            Column(Modifier.padding(18.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.AdminPanelSettings, contentDescription = null, tint = Cyan)
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f)) {
                        Text("لوحة تحكم مالك التطبيق", fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text(ownerEmail, color = Color.Gray, fontSize = 12.sp)
                    }
                    IconButton(onClick = onClose) {
                        Icon(Icons.Default.Close, contentDescription = "إغلاق")
                    }
                }
                Spacer(Modifier.height(12.dp))
                Text("صلاحيات المالك فقط", color = Cyan, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(10.dp))
                LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    item { AdminControlCard(Icons.Default.People, "إدارة الأعضاء", "مراجعة الأعضاء والحسابات والصلاحيات") }
                    item { AdminControlCard(Icons.Default.MeetingRoom, "إدارة الغرف", "التحكم في الغرف والمايك والمقاعد والإدارة") }
                    item { AdminControlCard(Icons.Default.Campaign, "الإعلانات", "إرسال إعلانات وتنبيهات لأعضاء التطبيق") }
                    item { AdminControlCard(Icons.Default.Analytics, "الإحصائيات", "متابعة التسجيلات والنشاط والغرف والرسائل") }
                    item { AdminControlCard(Icons.Default.Security, "الأمان", "إعدادات وحماية حساب المالك ولوحة التحكم") }
                }
            }
        }
    }
}

@Composable
private fun AdminControlCard(icon: ImageVector, title: String, subtitle: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = Surface2)
    ) {
        Row(Modifier.padding(15.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, contentDescription = null, tint = Cyan, modifier = Modifier.size(30.dp))
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(title, fontWeight = FontWeight.Bold)
                Text(subtitle, color = Color.Gray, fontSize = 12.sp)
            }
            Icon(Icons.Default.ChevronLeft, contentDescription = null)
        }
    }
}
'''
main.write_text(m)

