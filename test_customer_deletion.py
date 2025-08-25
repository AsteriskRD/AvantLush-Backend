#!/usr/bin/env python3
"""
Test script to verify customer deletion synchronization
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Customer, CustomUser, Profile
from django.db import transaction

def test_customer_deletion_sync():
    """Test that deleting a customer also deletes the associated user and profile"""
    
    print("🧪 Testing Customer Deletion Synchronization...")
    
    # Find a customer with an associated user
    customer_with_user = Customer.objects.filter(user__isnull=False).first()
    
    if not customer_with_user:
        print("❌ No customers with associated users found. Cannot test deletion sync.")
        return
    
    customer_id = customer_with_user.id
    customer_email = customer_with_user.email
    user_id = customer_with_user.user.id
    profile_id = customer_with_user.user.profile.id if hasattr(customer_with_user.user, 'profile') else None
    
    print(f"📋 Found customer: {customer_id} ({customer_email})")
    print(f"👤 Associated user: {user_id}")
    print(f"📸 Associated profile: {profile_id}")
    
    # Verify the records exist before deletion
    customer_exists = Customer.objects.filter(id=customer_id).exists()
    user_exists = CustomUser.objects.filter(id=user_id).exists()
    profile_exists = Profile.objects.filter(id=profile_id).exists() if profile_id else False
    
    print(f"✅ Before deletion - Customer: {customer_exists}, User: {user_exists}, Profile: {profile_exists}")
    
    if not all([customer_exists, user_exists, profile_exists]):
        print("❌ Some records don't exist before deletion. Cannot proceed with test.")
        return
    
    try:
        # Delete the customer (this should trigger our signal)
        print(f"🗑️ Deleting customer {customer_id}...")
        customer_with_user.delete()
        
        # Check if all related records were deleted
        customer_exists_after = Customer.objects.filter(id=customer_id).exists()
        user_exists_after = CustomUser.objects.filter(id=user_id).exists()
        profile_exists_after = Profile.objects.filter(id=profile_id).exists() if profile_id else False
        
        print(f"✅ After deletion - Customer: {customer_exists_after}, User: {user_exists_after}, Profile: {profile_exists_after}")
        
        # Test results
        if not any([customer_exists_after, user_exists_after, profile_exists_after]):
            print("🎉 SUCCESS: All related records were properly deleted!")
            return True
        else:
            print("❌ FAILURE: Some records still exist after deletion:")
            if customer_exists_after:
                print(f"   - Customer {customer_id} still exists")
            if user_exists_after:
                print(f"   - User {user_id} still exists")
            if profile_exists_after:
                print(f"   - Profile {profile_id} still exists")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during deletion test: {e}")
        return False

def test_customer_without_user_deletion():
    """Test that deleting a customer without an associated user works properly"""
    
    print("\n🧪 Testing Customer Deletion (No Associated User)...")
    
    # Find a customer without an associated user
    customer_without_user = Customer.objects.filter(user__isnull=True).first()
    
    if not customer_without_user:
        print("❌ No customers without associated users found. Cannot test this scenario.")
        return
    
    customer_id = customer_without_user.id
    customer_email = customer_without_user.email
    
    print(f"📋 Found customer without user: {customer_id} ({customer_email})")
    
    # Verify the record exists before deletion
    customer_exists = Customer.objects.filter(id=customer_id).exists()
    print(f"✅ Before deletion - Customer: {customer_exists}")
    
    try:
        # Delete the customer
        print(f"🗑️ Deleting customer {customer_id}...")
        customer_without_user.delete()
        
        # Check if it was deleted
        customer_exists_after = Customer.objects.filter(id=customer_id).exists()
        print(f"✅ After deletion - Customer: {customer_exists_after}")
        
        if not customer_exists_after:
            print("🎉 SUCCESS: Customer without user was properly deleted!")
            return True
        else:
            print("❌ FAILURE: Customer still exists after deletion")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during deletion test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Customer Deletion Synchronization Tests...\n")
    
    # Test 1: Customer with associated user
    test1_result = test_customer_deletion_sync()
    
    # Test 2: Customer without associated user
    test2_result = test_customer_without_user_deletion()
    
    print(f"\n📊 Test Results:")
    print(f"   Test 1 (Customer with User): {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"   Test 2 (Customer without User): {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Customer deletion synchronization is working properly.")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")
