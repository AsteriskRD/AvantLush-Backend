# 🎯 Product Variations API - Grouped by Size

## 📋 Overview

The new Product Variations API provides a **size-first approach** for managing product variants in your custom dashboard. Instead of individual variation records, variations are now grouped by size, making it easier for frontend developers to create intuitive size → color → price workflows.

## 🚀 New Endpoints

### 1. **GET** `/api/product-variations/grouped_by_size/`
**Get product variations grouped by size**

**Query Parameters:**
- `product_id` (required): The ID of the product

**Response Structure:**
```json
{
  "product_id": 42,
  "product_name": "Classic T-Shirt",
  "product_sku": "TSH-001",
  "variations": {
    "Small": {
      "size_id": 1,
      "colors": ["Red", "Blue", "Green"],
      "price": 40.00,
      "stock_quantity": 100
    },
    "Medium": {
      "size_id": 2,
      "colors": ["Red", "Black", "White"],
      "price": 45.00,
      "stock_quantity": 150
    },
    "Large": {
      "size_id": 3,
      "colors": ["Blue", "Black", "White"],
      "price": 50.00,
      "stock_quantity": 120
    }
  }
}
```

**Example Usage:**
```bash
GET /api/product-variations/grouped_by_size/?product_id=42
```

---

### 2. **POST** `/api/product-variations/add_size_variant/`
**Add a new size variant with colors and price**

**Request Body:**
```json
{
  "product_id": 42,
  "size": "Small",
  "colors": ["Red", "Blue", "Green"],
  "price": 40.00,
  "stock_quantity": 100
}
```

**Response:**
```json
{
  "message": "Size variant \"Small\" added successfully",
  "variation_id": 123,
  "size": "Small",
  "colors": ["Red", "Blue", "Green"],
  "price": 40.00,
  "stock_quantity": 100
}
```

**Frontend Workflow:**
1. Admin selects size (e.g., "Small")
2. Admin adds multiple color inputs (e.g., "Red", "Blue", "Green")
3. Admin enters price (e.g., $40.00)
4. Admin enters stock quantity (e.g., 100)
5. Admin clicks ➕ button
6. System creates the size variant

---

### 3. **PUT** `/api/product-variations/update_size_variant/`
**Update an existing size variant's colors, price, and stock**

**Request Body:**
```json
{
  "product_id": 42,
  "size": "Small",
  "colors": ["Red", "Blue", "Green", "Yellow"],
  "price": 42.00,
  "stock_quantity": 120
}
```

**Response:**
```json
{
  "message": "Size variant \"Small\" updated successfully",
  "size": "Small",
  "colors": ["Red", "Blue", "Green", "Yellow"],
  "price": 42.00,
  "stock_quantity": 120
}
```

---

### 4. **DELETE** `/api/product-variations/remove_size_variant/`
**Remove an entire size variant from a product**

**Request Body:**
```json
{
  "product_id": 42,
  "size": "Small"
}
```

**Response:**
```json
{
  "message": "Size variant \"Small\" removed successfully"
}
```

---

## 🔧 Technical Details

### **Database Structure**
- **Existing structure preserved**: All existing `ProductVariation` records remain intact
- **New grouping logic**: API groups variations by size for frontend consumption
- **Dynamic size creation**: Sizes are created automatically if they don't exist
- **Dynamic color creation**: Colors are created automatically if they don't exist

### **Price Calculation**
- **Base price**: Uses the product's base price from `Product.price`
- **Price adjustment**: Stored as `price_adjustment` in `ProductVariation`
- **Final price**: `product.price + price_adjustment`

### **Stock Management**
- **Per-size stock**: Each size variant has its own stock quantity
- **Individual tracking**: Stock is tracked at the variation level
- **Bulk operations**: Support for bulk stock updates

---

## 🎨 Frontend Implementation Guide

### **UI Components Needed**

1. **Size Input**
   - Text input or dropdown for size name
   - Auto-creates new sizes if they don't exist

2. **Color Inputs**
   - Multiple text inputs for color names
   - Auto-creates new colors if they don't exist
   - Dynamic addition/removal of color fields

3. **Price Input**
   - Numeric input for the price of this size variant

4. **Stock Input**
   - Numeric input for stock quantity

5. **Add Button (➕)**
   - Creates the size variant
   - Clears all inputs
   - Adds to the variants list

### **State Management**

```javascript
// Example state structure
const [variants, setVariants] = useState({
  "Small": {
    colors: ["Red", "Blue", "Green"],
    price: 40.00,
    stock_quantity: 100
  },
  "Medium": {
    colors: ["Red", "Black", "White"],
    price: 45.00,
    stock_quantity: 150
  }
});

const [currentInput, setCurrentInput] = useState({
  size: "",
  colors: [""],
  price: "",
  stock_quantity: ""
});
```

### **API Integration**

```javascript
// Add new size variant
const addSizeVariant = async (variantData) => {
  try {
    const response = await fetch('/api/product-variations/add_size_variant/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(variantData)
    });
    
    if (response.ok) {
      // Refresh variants list
      await loadVariants();
      // Clear inputs
      setCurrentInput({ size: "", colors: [""], price: "", stock_quantity: "" });
    }
  } catch (error) {
    console.error('Error adding variant:', error);
  }
};
```

---

## 🔒 Authentication & Permissions

- **All endpoints require authentication**: JWT token required
- **Admin access only**: `IsAdminUser` permission required
- **Product ownership**: Users can only manage variations for products they have access to

---

## 📱 Example Frontend Workflow

### **Step 1: Load Existing Variants**
```javascript
// Load product variations grouped by size
const loadVariants = async () => {
  const response = await fetch(`/api/product-variations/grouped_by_size/?product_id=${productId}`);
  const data = await response.json();
  setVariants(data.variations);
};
```

### **Step 2: Add New Variant**
1. User types "Small" in size field
2. User adds color inputs: "Red", "Blue", "Green"
3. User enters price: "40.00"
4. User enters stock: "100"
5. User clicks ➕ button
6. API creates the variant
7. UI refreshes and shows new variant

### **Step 3: Edit Existing Variant**
1. User clicks on existing variant
2. UI populates input fields with current values
3. User modifies colors, price, or stock
4. User clicks save
5. API updates the variant
6. UI refreshes with updated data

---

## 🚨 Error Handling

### **Common Error Responses**

```json
// Missing required fields
{
  "error": "product_id, size, colors, and price are required"
}

// Product not found
{
  "error": "Product not found"
}

// Size variant not found (for updates/deletes)
{
  "error": "No variation found for size \"Small\""
}
```

### **Frontend Error Handling**

```javascript
const handleApiError = (error) => {
  if (error.response?.data?.error) {
    // Show user-friendly error message
    setErrorMessage(error.response.data.error);
  } else {
    // Show generic error
    setErrorMessage('An unexpected error occurred');
  }
};
```

---

## 🔄 Migration Notes

### **What's Preserved**
- ✅ All existing `ProductVariation` records
- ✅ All existing `Size` and `Color` records
- ✅ All existing relationships and foreign keys
- ✅ All existing Django Admin functionality

### **What's New**
- 🆕 Grouped API endpoints for frontend consumption
- 🆕 Dynamic size/color creation
- 🆕 Simplified frontend workflow
- 🆕 Better UX for admin users

### **What's Unchanged**
- 🔒 Database schema remains the same
- 🔒 Django Admin interface unchanged
- 🔒 Existing API endpoints still work
- 🔒 All existing functionality preserved

---

## 🎯 Benefits

1. **Better UX**: Size-first approach is more intuitive
2. **Easier Management**: Group related variations together
3. **Dynamic Creation**: No need to pre-create sizes/colors
4. **Flexible Pricing**: Each size can have different pricing
5. **Stock Control**: Individual stock tracking per size
6. **Backward Compatible**: Existing system unchanged

---

## 🧪 Testing

Test the endpoints using:

```bash
# Test grouped view
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/product-variations/grouped_by_size/?product_id=1"

# Test adding variant
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"product_id": 1, "size": "Small", "colors": ["Red", "Blue"], "price": 40.00, "stock_quantity": 100}' \
     "http://localhost:8000/api/product-variations/add_size_variant/"
```

---

## 📞 Support

For questions or issues with the new Product Variations API:
- Check the Django logs for detailed error messages
- Verify authentication tokens are valid
- Ensure product IDs exist in the database
- Test with the provided examples above

---

*This API maintains full backward compatibility while providing a new, more intuitive interface for frontend developers.* 🚀
