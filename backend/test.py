import re
import time
from typing import Dict, List
from fuzzywuzzy import process, fuzz

class FuzzyOrderParser:
    """Parser with fuzzy matching for transcription errors - DEBUG VERSION"""
    
    def __init__(self):
        self.menu_items = {
            'burger': ['burger', 'classic burger'],
            'cheeseburger': ['cheeseburger'],
            'hamburger': ['hamburger'],
            'fries_small': ['fries', 'french fries', 'chips',"fry"],
            'fries_large': ['fries', 'french fries', 'chips',"fry"],
            'coke_small': ['coke', 'coca cola', 'cola'],
            'coke_large': ['coke', 'coca cola', 'cola'],
            'pepsi_can': ['pepsi'],
            'lemon_soda': ['lemon soda', 'sprite'],
            'chicken_sandwich': ['chicken sandwich', 'chicken'],
            'pizza_small': ['pizza'],
            'pizza_large': ['pizza']
        }
        
        self.all_keywords = []
        for item_id, keywords in self.menu_items.items():
            self.all_keywords.extend(keywords)
        self.all_keywords = list(set(self.all_keywords))
        
        self.quantity_map = {
            'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 
            'four': 4, 'five': 5, 'couple': 2, 'few': 3, "six": 6, 
            "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        
        self.prices = {
            'burger': 70, 'cheeseburger': 80, 'hamburger': 65,
            'fries_small': 40, 'fries_large': 60,
            'coke_small': 30, 'coke_large': 50,
            'pepsi_can': 30, 'lemon_soda': 50,
            'chicken_sandwich': 90,
            'pizza_small': 120, 'pizza_large': 180
        }
        
        self.debug = True  # Enable debug logging

    def parse_order(self, text: str) -> Dict:
        start_time = time.time()
        text = text.lower().strip()
        
        if not text or text.strip() == "":
            return self._empty_response(start_time, "Empty input")
        
        if self.debug:
            print(f"\n{'='*60}")
            print(f"🔍 PARSING: '{text}'")
            print(f"{'='*60}")
        
        items = self._unified_parse(text)
        
        if self.debug:
            print(f"\n📊 BEFORE MERGE: {len(items)} items")
            for idx, item in enumerate(items):
                print(f"   [{idx}] {item['quantity']}x {item['name']} (id: {item['id']})")
        
        items = self._merge_duplicate_items(items)
        
        if self.debug:
            print(f"\n📊 AFTER MERGE: {len(items)} items")
            for idx, item in enumerate(items):
                print(f"   [{idx}] {item['quantity']}x {item['name']} (id: {item['id']})")
            print(f"{'='*60}\n")
        
        return self._build_response(items, text, start_time)
    
    def _unified_parse(self, text: str) -> List[Dict]:
        """Unified parser with detailed debugging"""
        items = []
        words = re.findall(r'\b\w+\b', text)
        processed_indices = set()
        
        if self.debug:
            print(f"\n📝 WORDS: {words}")
        
        i = 0
        while i < len(words):
            if i in processed_indices:
                if self.debug:
                    print(f"   [i={i}] '{words[i]}' -> ALREADY PROCESSED, skipping")
                i += 1
                continue
            
            word = words[i]
            
            # Skip common filler words
            if word in ['i', 'want', 'get', 'have', 'please', 'can', 'and', 'the', 'of', 'order']:
                if self.debug:
                    print(f"   [i={i}] '{word}' -> FILLER WORD, skipping")
                i += 1
                continue
            
            # Check if this is a quantity word
            if word in self.quantity_map:
                quantity = self.quantity_map[word]
                processed_indices.add(i)
                
                if self.debug:
                    print(f"   [i={i}] '{word}' -> QUANTITY: {quantity}")
                
                # Look ahead for the item
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    processed_indices.add(i + 1)
                    
                    if self.debug:
                        print(f"   [i={i+1}] '{next_word}' -> LOOKING FOR ITEM MATCH")
                    
                    # Try exact match first
                    found_items = self._try_exact_match(next_word, text, quantity)
                    
                    if self.debug:
                        print(f"      ✓ Exact match returned {len(found_items)} items")
                    
                    # If no exact match, try fuzzy
                    if not found_items:
                        best_match, score = process.extractOne(next_word, self.all_keywords, scorer=fuzz.ratio)
                        if score > 70:
                            if self.debug:
                                print(f"      ✓ Fuzzy match: '{next_word}' -> '{best_match}' (score: {score})")
                            found_items = self._find_menu_items_with_size(best_match, text, quantity, exact_match=False)
                            if self.debug:
                                print(f"      ✓ Fuzzy match returned {len(found_items)} items")
                        else:
                            if self.debug:
                                print(f"      ✗ No fuzzy match (score {score} < 70)")
                    
                    if found_items:
                        items.extend(found_items)
                        if self.debug:
                            print(f"      ➕ ADDED {len(found_items)} items (Total now: {len(items)})")
                    
                    i += 2
                    continue
                else:
                    if self.debug:
                        print(f"      ✗ No word after quantity")
                    i += 1
                    continue
            
            # Not a quantity word - try to match as an item with quantity 1
            if self.debug:
                print(f"   [i={i}] '{word}' -> TRYING AS ITEM (qty=1)")
            
            # Try exact match first
            found_items = self._try_exact_match(word, text, 1)
            
            if self.debug:
                print(f"      ✓ Exact match returned {len(found_items)} items")
            
            # If no exact match, try fuzzy
            if not found_items:
                best_match, score = process.extractOne(word, self.all_keywords, scorer=fuzz.ratio)
                if score > 70:
                    if self.debug:
                        print(f"      ✓ Fuzzy match: '{word}' -> '{best_match}' (score: {score})")
                    found_items = self._find_menu_items_with_size(best_match, text, 1, exact_match=False)
                    if self.debug:
                        print(f"      ✓ Fuzzy match returned {len(found_items)} items")
                else:
                    if self.debug:
                        print(f"      ✗ No fuzzy match (score {score} < 70)")
            
            if found_items:
                processed_indices.add(i)
                items.extend(found_items)
                if self.debug:
                    print(f"      ➕ ADDED {len(found_items)} items (Total now: {len(items)})")
            else:
                if self.debug:
                    print(f"      ✗ No match found")
            
            i += 1
        
        return items
    
    def _try_exact_match(self, word: str, full_text: str, quantity: int) -> List[Dict]:
        """Try to find exact matches for a word"""
        if self.debug:
            print(f"         [EXACT] Checking '{word}' in menu keywords...")
        
        for item_id, keywords in self.menu_items.items():
            if word in keywords:
                if self.debug:
                    print(f"         [EXACT] ✓ Found in '{item_id}' keywords: {keywords}")
                return self._find_menu_items_with_size(word, full_text, quantity, exact_match=True)
        
        if self.debug:
            print(f"         [EXACT] ✗ Not found in any menu keywords")
        return []
    
    def _find_menu_items_with_size(self, word: str, full_text: str, quantity: int, exact_match: bool = True) -> List[Dict]:
        """Find menu items with size handling - FIXED to prevent duplicates"""
        if self.debug:
            print(f"         [FIND] Looking for '{word}' with qty={quantity}, exact={exact_match}")
        
        size = self._extract_size(full_text)
        
        if self.debug:
            print(f"         [FIND] Detected size: {size}")
        
        # Find the first matching item
        for item_id, keywords in self.menu_items.items():
            if word in keywords or (not exact_match and any(phrase == word for phrase in keywords)):
                if self.debug:
                    print(f"         [FIND] Match in item_id='{item_id}', keywords={keywords}")
                
                # Check if this is a size-dependent item
                if any(base_item in item_id for base_item in ['fries', 'coke', 'pizza']):
                    final_item_id = self._resolve_size_dependent_item(item_id, size)
                    if self.debug:
                        print(f"         [FIND] ➕ Creating item: {quantity}x {final_item_id}")
                    
                    return [{
                        "id": final_item_id,
                        "name": self._get_display_name(final_item_id),
                        "quantity": quantity,
                        "size": size or ("small" if "small" in final_item_id else "large"),
                        "price": self.prices[final_item_id],
                        "total_price": quantity * self.prices[final_item_id],
                        "match_type": "exact" if exact_match else "fuzzy"
                    }]
                else:
                    if self.debug:
                        print(f"         [FIND] ➕ Creating item: {quantity}x {item_id}")
                    
                    return [{
                        "id": item_id,
                        "name": self._get_display_name(item_id),
                        "quantity": quantity,
                        "size": "standard",
                        "price": self.prices[item_id],
                        "total_price": quantity * self.prices[item_id],
                        "match_type": "exact" if exact_match else "fuzzy"
                    }]
        
        if self.debug:
            print(f"         [FIND] No match found, returning empty list")
        
        return []
    
    def _resolve_size_dependent_item(self, item_id: str, size: str) -> str:
        if 'fries' in item_id:
            return 'fries_large' if size == 'large' else 'fries_small'
        elif 'coke' in item_id:
            return 'coke_large' if size == 'large' else 'coke_small'
        elif 'pizza' in item_id:
            return 'pizza_large' if size == 'large' else 'pizza_small'
        return item_id
    
    def _get_display_name(self, item_id: str) -> str:
        display_names = {
            'burger': 'Classic Burger', 'cheeseburger': 'Cheeseburger', 'hamburger': 'Hamburger',
            'fries_small': 'French Fries (Small)', 'fries_large': 'French Fries (Large)',
            'coke_small': 'Coke (Small)', 'coke_large': 'Coke (Large)',
            'pepsi_can': 'Pepsi (Can)', 'lemon_soda': 'Lemon Soda',
            'chicken_sandwich': 'Chicken Sandwich',
            'pizza_small': 'Pizza (Small)', 'pizza_large': 'Pizza (Large)'
        }
        return display_names.get(item_id, item_id)
    
    def _extract_size(self, text: str) -> str:
        sizes = {'small': 'small', 'medium': 'medium', 'large': 'large'}
        for size in sizes:
            if size in text:
                return sizes[size]
        return None
    
    def _merge_duplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Merge duplicate items by ID"""
        if self.debug:
            print(f"\n🔄 MERGING DUPLICATES:")
        
        merged = {}
        for item in items:
            key = item['id']
            if key in merged:
                if self.debug:
                    print(f"   Found duplicate '{key}': {merged[key]['quantity']} + {item['quantity']} = {merged[key]['quantity'] + item['quantity']}")
                merged[key]['quantity'] += item['quantity']
                merged[key]['total_price'] += item['total_price']
            else:
                if self.debug:
                    print(f"   New item '{key}': {item['quantity']}x")
                merged[key] = item.copy()
        return list(merged.values())
    
    def _build_response(self, items: List, text: str, start_time: float) -> Dict:
        processing_time = round((time.time() - start_time) * 1000, 2)
        total_order_value = sum(item['total_price'] for item in items)
        
        confidence = "high" if items else "low"
        if any(item.get('match_type') == 'fuzzy' for item in items):
            confidence = "medium"
        
        return {
            "items": items,
            "confidence": confidence,
            "processing_time_ms": processing_time,
            "original_text": text,
            "items_count": len(items),
            "total_order_value": total_order_value,
            "currency": "INR"
        }
    
    def _empty_response(self, start_time: float, reason: str) -> Dict:
        processing_time = round((time.time() - start_time) * 1000, 2)
        return {
            "items": [], "confidence": "low", "processing_time_ms": processing_time,
            "original_text": "", "error": reason, "items_count": 0,
            "total_order_value": 0, "currency": "INR"
        }

# Create parser instance
parser = FuzzyOrderParser()
