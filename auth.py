import streamlit as st
import time

class KeyVault:
    def __init__(self):
        # Initialize keys if not present
        if 'groq_keys' not in st.session_state:
            st.session_state.groq_keys = []
        if 'key_blacklist' not in st.session_state:
            st.session_state.key_blacklist = {} # {key: unblacklist_time}
        if 'api_index' not in st.session_state:
            st.session_state.api_index = 0

    def update_keys(self, keys: list[str]):
        """Update valid keys, stripping whitespace."""
        valid_keys = [k.strip() for k in keys if k and k.strip()]
        st.session_state.groq_keys = valid_keys

    def get_next_key(self) -> str | None:
        """Returns the next available unblacklisted key using round-robin."""
        keys = st.session_state.groq_keys
        if not keys:
            return None

        current_time = time.time()
        
        # Clean up expired blacklisted keys
        for k in list(st.session_state.key_blacklist.keys()):
            if st.session_state.key_blacklist[k] < current_time:
                del st.session_state.key_blacklist[k]

        available_keys = [k for k in keys if k not in st.session_state.key_blacklist]
        
        if not available_keys:
            return None # All keys blacklisted

        # Use index to get the next key in available keys, handling wrap-around
        # To strictly follow the index across updates, we take api_index % len(available_keys)
        # But if the list shrinks, we just use modulo.
        selected_key = available_keys[st.session_state.api_index % len(available_keys)]
        st.session_state.api_index += 1
        
        return selected_key

    def blacklist_key(self, key: str, duration_seconds: int = 60):
        """Blacklist a key for a given duration due to rate limit."""
        if key in st.session_state.groq_keys:
            st.session_state.key_blacklist[key] = time.time() + duration_seconds

vault = KeyVault()
