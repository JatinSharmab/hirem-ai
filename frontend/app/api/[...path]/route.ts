import { NextRequest } from "next/server";
import { handleBff } from "@/lib/api/bff";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;
type Context = { params: Promise<{ path: string[] }> };
async function handler(request: NextRequest, context: Context) {
  const { path } = await context.params;
  return handleBff(request, path);
}
export { handler as GET, handler as POST, handler as PATCH, handler as DELETE };
