import prisma from '../src/lib/prisma'
import { v4 as uuidv4 } from 'uuid'

const PERMISSIONS = [
  // 1. Authentication & Security (6)
  "auth.login", "auth.logout", "auth.pin_setup", "auth.biometric_enable", "auth.session_manage", "auth.reset_access",
  // 2. Role & Permission Management (6)
  "role.view", "role.create", "role.edit", "role.delete", "role.assign_permissions", "role.manage_users",
  // 3. Lead Management (8)
  "lead.view", "lead.create", "lead.edit", "lead.delete", "lead.assign", "lead.import", "lead.export", "lead.change_status",
  // 4. Rate Calculator (6)
  "rate.view", "rate.calculate", "rate.edit_rules", "rate.manage_addons", "rate.configure_tables", "rate.export",
  // 5. RTO Work Management (6)
  "rto.view", "rto.create", "rto.edit", "rto.delete", "rto.update_status", "rto.track_payment",
  // 6. Fitness Work Management (6)
  "fitness.view", "fitness.create", "fitness.edit", "fitness.delete", "fitness.update_status", "fitness.track_payment",
  // 7. Claims Management (6)
  "claims.view", "claims.create", "claims.edit", "claims.delete", "claims.update_status", "claims.upload_documents",
  // 8. Accounts & Finance (7)
  "accounts.view", "accounts.create_entry", "accounts.edit_entry", "accounts.delete_entry", "accounts.view_reports", "accounts.export", "accounts.manage_salary",
  // 9. HR Management (7)
  "hr.view", "hr.create", "hr.edit", "hr.delete", "hr.manage_attendance", "hr.manage_leave", "hr.view_performance",
  // 10. Loan Department (6)
  "loan.view", "loan.create", "loan.edit", "loan.delete", "loan.update_status", "loan.track_conversion",
  // 11. CRM System (6)
  "crm.view", "crm.create", "crm.edit", "crm.delete", "crm.manage_followups", "crm.view_revenue",
  // 12. Customer Visit Module (6)
  "visit.view", "visit.create", "visit.edit", "visit.delete", "visit.track_location", "visit.manage_followups",
  // 13. Data Management (6)
  "data.view", "data.create", "data.edit", "data.delete", "data.approve_changes", "data.manage_documents",
  // 14. Quotation System (6)
  "quotation.view", "quotation.create", "quotation.edit", "quotation.delete", "quotation.generate_pdf", "quotation.share",
  // 15. Dashboard & Analytics (4)
  "dashboard.view_agent", "dashboard.view_manager", "dashboard.view_admin", "dashboard.export",
  // 16. Notifications (4)
  "notification.view", "notification.send", "notification.manage", "notification.configure",
  // 17. Templates (WhatsApp/SMS) (4)
  "template.view", "template.create", "template.edit", "template.delete",
  // 18. Admin Panel / System Config (2)
  "system.settings_manage", "system.audit_logs_view"
]

const ROLES = [
  "Super Admin", "Admin", "Manager", "Sales Executive", "Telecaller", "Field Executive", "RTO Executive",
  "Claims Executive", "Loan Executive", "CRM Executive", "Accountant", "HR Manager", "Viewer"
]

async function main() {
  console.log('🌱 Starting seed with 102 permissions...')

  // 1. Create all permissions
  const permissionMap: Record<string, any> = {}
  
  for (const name of PERMISSIONS) {
    const perm = await prisma.permission.upsert({
      where: { name },
      update: {},
      create: {
        id: uuidv4(),
        name,
        description: `Can ${name.split('.')[1]} ${name.split('.')[0]}`
      }
    })
    permissionMap[name] = perm
  }

  const allPermissions = Object.values(permissionMap)

  // 2. Create roles and assign permissions
  for (const roleName of ROLES) {
    let rolePermissions: any[] = []

    if (roleName === "Super Admin") {
      rolePermissions = allPermissions
    } else if (roleName === "Admin") {
      rolePermissions = allPermissions.filter(p => !p.name.includes(".delete"))
    } else {
      // Default to view permissions
      rolePermissions = allPermissions.filter(p => p.name.includes(".view"))
    }

    await prisma.role.upsert({
      where: { name: roleName },
      update: {
        permissions: {
          set: rolePermissions.map(p => ({ id: p.id }))
        }
      },
      create: {
        id: uuidv4(),
        name: roleName,
        permissions: {
          connect: rolePermissions.map(p => ({ id: p.id }))
        }
      }
    })
  }

  console.log(`✅ Seeding complete! Created/Updated ${PERMISSIONS.length} permissions and ${ROLES.length} roles.`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
