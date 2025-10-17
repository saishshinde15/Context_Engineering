"""
Context Offloading Tools for CrewAI

This module implements scratchpad tools for context offloading:
- ScratchpadWriteTool: Write notes to persistent scratchpad
- ScratchpadReadTool: Read notes from persistent scratchpad
- UserPreferenceTool: Read user preferences from knowledge base
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path

# Module-level constants for file paths
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"
KNOWLEDGE_DIR.mkdir(exist_ok=True)
SCRATCHPAD_FILE = KNOWLEDGE_DIR / "scratchpad.json"
PREFERENCE_FILE = KNOWLEDGE_DIR / "user_preference.txt"


class ScratchpadWriteInput(BaseModel):
    """Input schema for ScratchpadWriteTool."""
    notes: str = Field(..., description="Notes to save to the scratchpad for future reference")
    category: str = Field(
        default="general",
        description="Category for organizing notes (e.g., 'research_plan', 'findings', 'summary')"
    )


class ScratchpadReadInput(BaseModel):
    """Input schema for ScratchpadReadTool."""
    reasoning: str = Field(
        ...,
        description="Explain why you need to read the scratchpad (forces intentional retrieval)"
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional: specific category to read from (None = read all)"
    )


class UserPreferenceInput(BaseModel):
    """Input schema for UserPreferenceTool."""
    query: str = Field(..., description="What user preference information are you looking for?")


class ScratchpadWriteTool(BaseTool):
    """
    Tool for writing notes to a persistent scratchpad.
    
    This implements context offloading by storing information outside the LLM's
    context window in a JSON file that persists across agent runs.
    
    Benefits:
    - Avoids context rot (information degradation deep in context)
    - Enables information reuse across multiple tasks
    - Creates an audit trail of agent thinking
    - Implements "recitation effect" by moving info to end of context
    """
    
    name: str = "scratchpad_write"
    description: str = (
        "Write notes to the persistent scratchpad for future reference. "
        "Use this to offload important information, research plans, findings, "
        "or summaries that you want to remember across different parts of your task. "
        "This helps avoid context window limitations and keeps important info accessible."
    )
    args_schema: Type[BaseModel] = ScratchpadWriteInput
    
    def _run(self, notes: str, category: str = "general") -> str:
        """
        Write notes to the scratchpad file.
        
        Args:
            notes: Content to write
            category: Organizational category
            
        Returns:
            Confirmation message
        """
        try:
            # Load existing scratchpad
            if SCRATCHPAD_FILE.exists():
                with open(SCRATCHPAD_FILE, 'r') as f:
                    scratchpad = json.load(f)
            else:
                scratchpad = {}
            
            # Update category
            if category not in scratchpad:
                scratchpad[category] = []
            
            # Append new notes with timestamp
            from datetime import datetime
            entry = {
                "timestamp": datetime.now().isoformat(),
                "notes": notes
            }
            scratchpad[category].append(entry)
            
            # Save back to file
            with open(SCRATCHPAD_FILE, 'w') as f:
                json.dump(scratchpad, f, indent=2)
            
            return f"✅ Successfully wrote to scratchpad under category '{category}'. Total entries in this category: {len(scratchpad[category])}"
            
        except Exception as e:
            return f"❌ Error writing to scratchpad: {str(e)}"
class ScratchpadReadTool(BaseTool):
    """
    Tool for reading notes from the persistent scratchpad.
    
    Retrieves previously offloaded context, effectively "refreshing" its position
    by bringing it to the end of the context window.
    """
    
    name: str = "scratchpad_read"
    description: str = (
        "Read notes from the persistent scratchpad. Use this to retrieve information "
        "you or other agents previously saved. This is essential for building upon "
        "previous work and maintaining context across different parts of your task."
    )
    args_schema: Type[BaseModel] = ScratchpadReadInput
    
    def _run(self, reasoning: str, category: Optional[str] = None) -> str:
        """
        Read notes from the scratchpad file.
        
        Args:
            reasoning: Why the agent needs this information
            category: Optional specific category to read
            
        Returns:
            Scratchpad contents or error message
        """
        try:
            if not SCRATCHPAD_FILE.exists():
                return "📝 Scratchpad is empty. No notes have been saved yet."
            
            with open(SCRATCHPAD_FILE, 'r') as f:
                scratchpad = json.load(f)
            
            if not scratchpad:
                return "📝 Scratchpad is empty. No notes have been saved yet."
            
            # Format output
            output = "📚 **Scratchpad Contents**\n\n"
            
            if category:
                # Read specific category
                if category in scratchpad:
                    output += f"**Category: {category}**\n"
                    for i, entry in enumerate(scratchpad[category], 1):
                        output += f"\n{i}. [{entry['timestamp']}]\n{entry['notes']}\n"
                else:
                    output += f"No notes found in category '{category}'."
            else:
                # Read all categories
                for cat, entries in scratchpad.items():
                    output += f"\n**Category: {cat}** ({len(entries)} entries)\n"
                    for i, entry in enumerate(entries, 1):
                        output += f"\n{i}. [{entry['timestamp']}]\n{entry['notes']}\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error reading scratchpad: {str(e)}"


class UserPreferenceTool(BaseTool):
    """
    Tool for reading user preferences from the knowledge base.
    
    Demonstrates context offloading from external files - user preferences
    are stored outside the context and retrieved on-demand.
    """
    
    name: str = "read_user_preferences"
    description: str = (
        "Read user preferences and requirements from the knowledge base. "
        "Use this to understand user context, preferences, or specific requirements "
        "that should guide your research and analysis."
    )
    args_schema: Type[BaseModel] = UserPreferenceInput
    
    def _run(self, query: str) -> str:
        """
        Read user preferences from file.
        
        Args:
            query: What information is being sought
            
        Returns:
            User preferences or error message
        """
        try:
            if not PREFERENCE_FILE.exists():
                return "⚠️ No user preferences file found. Creating default..."
            
            with open(PREFERENCE_FILE, 'r') as f:
                preferences = f.read()
            
            if not preferences.strip():
                return "📝 User preferences file is empty."
            
            return f"👤 **User Preferences**\n\n{preferences}"
            
        except Exception as e:
            return f"❌ Error reading user preferences: {str(e)}"
