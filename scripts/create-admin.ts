import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function createAdmin() {
  const email = process.env.ADMIN_EMAIL || 'admin@carbon6.io';
  const password = process.env.ADMIN_PASSWORD || 'ChangeMe123!';
  
  const passwordHash = await bcrypt.hash(password, 12);
  
  const admin = await prisma.user.create({
    data: {
      email,
      passwordHash,
      role: 'ADMIN',
      clearance: 'L5-BLACK',
      status: 'ACTIVE',
      emailVerified: true,
    },
  });
  
  console.log('✓ Admin created:', admin.email);
}

createAdmin()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
