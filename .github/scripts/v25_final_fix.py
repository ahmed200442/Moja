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

# Kotlin 2.2 needs explicit RPC result types for side-effect calls.
s=s.replace(
    """        })
    }

    suspend fun markNotificationRead""",
    """        }).decodeSingle<Unit>()
    }

    suspend fun markNotificationRead"""
)
s=s.replace(
    'client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) })',
    'client.postgrest.rpc("mawja_mark_notification_read", buildJsonObject { put("p_notification_id", notificationId) }).decodeSingle<Unit>()'
)
s=s.replace(
    'client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) })',
    'client.postgrest.rpc("mawja_mark_conversation_read", buildJsonObject { put("p_conversation_id", conversationId) }).decodeSingle<Unit>()'
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
