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

# Give the RPC response type explicitly; these calls are used for side effects.
s=s.replace(
    'client.postgrest.rpc("mawja_register_push_token",',
    'client.postgrest.rpc<JsonObject>("mawja_register_push_token",'
)
s=s.replace(
    'client.postgrest.rpc("mawja_mark_notification_read",',
    'client.postgrest.rpc<JsonObject>("mawja_mark_notification_read",'
)
s=s.replace(
    'client.postgrest.rpc("mawja_mark_conversation_read",',
    'client.postgrest.rpc<JsonObject>("mawja_mark_conversation_read",'
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
