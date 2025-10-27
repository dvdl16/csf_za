#!/bin/bash

# This is used in pacakge.json to block the help pages from public access, and copy the assets to the correct directory

AUTH_CONTENT="import frappe
from frappe import _

if frappe.session.user=='Guest':
    frappe.throw(_(\"You need to be logged in to access this page\"), frappe.PermissionError)"

for file in csf_za/www/csf_za_*.html; do
  if [ -f "$file" ]; then
    py_file="csf_za/www/$(basename "$file" .html).py"
    echo "$AUTH_CONTENT" > "$py_file"
  fi
done

rm -rf ./csf_za/public/chunks
mv ./csf_za/www/assets/csf_za/chunks ./csf_za/public/.
mv ./csf_za/www/assets/csf_za/*.js ./csf_za/public/.
mv ./csf_za/www/assets/csf_za/*.css ./csf_za/public/.