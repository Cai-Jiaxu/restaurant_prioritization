import { MetadataRoute } from 'next';
import { siteConfig } from '@/data/config/site.settings';

export const dynamic = 'force-static';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: siteConfig.siteUrl,
      lastModified: new Date().toISOString().split('T')[0],
    },
  ];
}
