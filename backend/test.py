import re
import json
import time
from typing import Dict, List

class SimpleOrderParser:
    """Parser optimized for your exact restaurant menu"""
    
    def __init__(self):
        # Updated to match your product IDs exactly
        self.menu_items = {
            'burger': ['burger', 'classic burger'],
            'cheeseburger': ['cheeseburger'],
            'hamburger': ['hamburger'],
            'fries_small': ['fries', 'french fries', 'chips'],  # Will be adjusted by size
            'fries_large': ['fries', 'french fries', 'chips'],  # Will be adjusted by size
            'coke_small': ['coke', 'coca cola', 'cola'],
            'coke_large': ['coke', 'coca cola', 'cola'],
            'pepsi_can': ['pepsi'],
            'lemon_soda': ['lemon soda', 'sprite'],  # Mapping sprite to lemon_soda
            'chicken_sandwich': ['chicken sandwich', 'chicken'],
            'pizza_small': ['pizza'],
            'pizza_large': ['pizza']
        }
        
        self.quantity_map = {
            'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 
            'four': 4, 'five': 5, 'couple': 2, 'few': 3, "six": 6, 
            "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        
        # Price mapping for your products
        self.prices = {
            'burger': 70,
            'cheeseburger': 80,
            'hamburger': 65,
            'fries_small': 40,
            'fries_large': 60,
            'coke_small': 30,
            'coke_large': 50,
            'pepsi_can': 30,
            'lemon_soda': 50,
            'chicken_sandwich': 90,
            'pizza_small': 120,
            'pizza_large': 180
        }

    def parse_order(self, text: str) -> Dict:
        """Parse order and return items matching your product IDs"""
        start_time = time.time()
        text = text.lower().strip()
        items = []
        
        # Handle empty input
        if not text or text.strip() == "":
            return self._empty_response(start_time, "Empty input")
        
        words = re.findall(r'\b\w+\b', text)
        i = 0
        
        while i < len(words):
            word = words[i]
            quantity = 1
            
            # Check for quantity
            if word in self.quantity_map:
                quantity = self.quantity_map[word]
                i += 1
                if i >= len(words):
                    break
                word = words[i]
            
            # Check for menu items with size handling
            found_items = self._find_menu_items_with_size(word, text, quantity)
            items.extend(found_items)
            
            i += 1
        
        # Remove duplicates and merge quantities
        items = self._merge_duplicate_items(items)
        
        return self._build_response(items, text, start_time)
    
    def _find_menu_items_with_size(self, word: str, full_text: str, quantity: int) -> List[Dict]:
        """Find menu items with proper size handling"""
        found_items = []
        size = self._extract_size(full_text)
        
        # Special handling for size-dependent items
        size_dependent_items = {
            'fries': ['fries_small', 'fries_large'],
            'coke': ['coke_small', 'coke_large'], 
            'pizza': ['pizza_small', 'pizza_large']
        }
        
        # Check each menu item
        for item_id, keywords in self.menu_items.items():
            if word in keywords or any(phrase in full_text for phrase in keywords if ' ' in phrase):
                
                # Handle size-dependent items
                if any(base_item in item_id for base_item in ['fries', 'coke', 'pizza']):
                    final_item_id = self._resolve_size_dependent_item(item_id, size)
                    if final_item_id:
                        found_items.append({
                            "id": final_item_id,
                            "name": self._get_display_name(final_item_id),
                            "quantity": quantity,
                            "size": size or ("small" if "small" in final_item_id else "large"),
                            "price": self.prices[final_item_id],
                            "total_price": quantity * self.prices[final_item_id]
                        })
                else:
                    # Regular items (burgers, sandwich, etc.)
                    found_items.append({
                        "id": item_id,
                        "name": self._get_display_name(item_id),
                        "quantity": quantity,
                        "size": "standard",  # No size for burgers/sandwiches
                        "price": self.prices[item_id],
                        "total_price": quantity * self.prices[item_id]
                    })
        
        return found_items
    
    def _resolve_size_dependent_item(self, item_id: str, size: str) -> str:
        """Resolve the actual product ID based on size"""
        if 'fries' in item_id:
            return 'fries_large' if size == 'large' else 'fries_small'
        elif 'coke' in item_id:
            return 'coke_large' if size == 'large' else 'coke_small'
        elif 'pizza' in item_id:
            return 'pizza_large' if size == 'large' else 'pizza_small'
        return item_id
    
    def _get_display_name(self, item_id: str) -> str:
        """Get display name for each product ID"""
        display_names = {
            'burger': 'Classic Burger',
            'cheeseburger': 'Cheeseburger',
            'hamburger': 'Hamburger',
            'fries_small': 'French Fries (Small)',
            'fries_large': 'French Fries (Large)',
            'coke_small': 'Coke (Small)',
            'coke_large': 'Coke (Large)',
            'pepsi_can': 'Pepsi (Can)',
            'lemon_soda': 'Lemon Soda',
            'chicken_sandwich': 'Chicken Sandwich',
            'pizza_small': 'Pizza (Small)',
            'pizza_large': 'Pizza (Large)'
        }
        return display_names.get(item_id, item_id)
    
    def _extract_size(self, text: str) -> str:
        """Extract size from text"""
        sizes = {'small': 'small', 'medium': 'medium', 'large': 'large'}
        for size in sizes:
            if size in text:
                return sizes[size]
        return None
    
    def _merge_duplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Merge duplicate items and sum quantities"""
        merged = {}
        for item in items:
            key = item['id']
            if key in merged:
                merged[key]['quantity'] += item['quantity']
                merged[key]['total_price'] += item['total_price']
            else:
                merged[key] = item.copy()
        return list(merged.values())
    
    def _build_response(self, items: List, text: str, start_time: float) -> Dict:
        """Build standardized response"""
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        # Calculate total order value
        total_order_value = sum(item['total_price'] for item in items)
        
        # Determine confidence
        if items:
            confidence = "high"
        elif any(word in text for word in ['want', 'get', 'have', 'order']):
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "items": items,
            "confidence": confidence,
            "processing_time_ms": processing_time,
            "original_text": text,
            "items_count": len(items),
            "total_order_value": total_order_value,
            "currency": "INR"  # Assuming Indian Rupees from your prices
        }
    
    def _empty_response(self, start_time: float, reason: str) -> Dict:
        """Response for empty input"""
        processing_time = round((time.time() - start_time) * 1000, 2)
        return {
            "items": [],
            "confidence": "low",
            "processing_time_ms": processing_time,
            "original_text": "",
            "error": reason,
            "items_count": 0,
            "total_order_value": 0,
            "currency": "INR"
        }

# Create parser instance
parser = SimpleOrderParser()

def main():
    """Test the parser with your exact menu"""
    test_cases = [
        "i want a classic burger and two cokes",
        "can I get three large pizzas",
        "one chicken sandwich please",
        "just some small fries", 
        "I'll have a cheeseburger and large fries",
        "not sure, maybe a pizza",
        "two hamburgers and one large coke",
        "give me a pepsi and lemon soda",
        "i want food",  # No specific items
        "hello",  # Edge case
        ""  # Empty case
    ]
    
    print("🧪 RESTAURANT PARSER TEST")
    print("=" * 60)
    
    for i, order in enumerate(test_cases, 1):
        print(f"\n{i}. 📝 Input: '{order}'")
        result = parser.parse_order(order)
        
        print(f"   🎯 Confidence: {result['confidence']}")
        print(f"   ⚡ Speed: {result['processing_time_ms']}ms")
        print(f"   💰 Total: ₹{result['total_order_value']}")
        print(f"   📦 Items ({result['items_count']}):")
        
        if result['items']:
            for item in result['items']:
                size_display = f" ({item['size']})" if item['size'] != 'standard' else ""
                print(f"      - {item['quantity']}x {item['name']}{size_display} = ₹{item['total_price']}")
        else:
            print("      ❗ No items detected")

if __name__ == "__main__":
    main()
