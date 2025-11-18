"""
Contact Extractor - Extracts emails, names, and company info from scraped websites
Uses regex patterns and NLP to find real contact data
"""
import re
from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ContactExtractor:
    """
    Extracts contact information from HTML/text content
    - Email addresses
    - Names (with role detection)
    - Phone numbers
    - LinkedIn profiles
    - Company information
    """

    # Email regex pattern
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Phone patterns (US and international)
    PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    # LinkedIn profile pattern
    LINKEDIN_PATTERN = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'

    # Common job titles/roles
    JOB_TITLES = [
        'ceo', 'cto', 'cfo', 'coo', 'vp', 'director', 'manager', 'head of',
        'founder', 'co-founder', 'president', 'chief', 'lead', 'senior',
        'engineer', 'developer', 'designer', 'product manager', 'sales',
        'marketing', 'operations'
    ]

    def extract_emails(self, text: str) -> Set[str]:
        """
        Extract all email addresses from text

        Args:
            text: Text content to search

        Returns:
            Set of unique email addresses
        """
        emails = set(re.findall(self.EMAIL_PATTERN, text, re.IGNORECASE))

        # Filter out common invalid patterns
        filtered_emails = {
            email for email in emails
            if not any(invalid in email.lower() for invalid in [
                'example.com', 'test.com', 'domain.com', 'email.com',
                'yourcompany', 'company.com', 'sampledata'
            ])
        }

        return filtered_emails

    def extract_phones(self, text: str) -> Set[str]:
        """Extract phone numbers from text"""
        phones = set(re.findall(self.PHONE_PATTERN, text))
        # Clean up formatting
        cleaned = {self._clean_phone(phone) for phone in phones if phone}
        return {p for p in cleaned if len(p) >= 10}

    def extract_linkedin_profiles(self, text: str) -> Set[str]:
        """Extract LinkedIn profile URLs"""
        return set(re.findall(self.LINKEDIN_PATTERN, text, re.IGNORECASE))

    def extract_names_with_roles(self, html: str) -> List[Dict[str, str]]:
        """
        Extract names with their roles from HTML

        Args:
            html: HTML content

        Returns:
            List of dicts with 'name' and 'role'
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # Look for common team/about page patterns
        team_sections = soup.find_all(['div', 'section'], class_=re.compile(r'team|about|staff|people', re.I))

        for section in team_sections:
            # Find names and titles in structured content
            names = section.find_all(['h2', 'h3', 'h4', 'strong', 'b'])

            for name_elem in names:
                name_text = name_elem.get_text(strip=True)

                # Check if looks like a name (2-4 words, capitalized)
                if self._looks_like_name(name_text):
                    # Look for role in next siblings or parent
                    role = self._find_role_near_name(name_elem)

                    results.append({
                        'name': name_text,
                        'role': role or 'Team Member'
                    })

        # Deduplicate
        seen = set()
        unique_results = []
        for item in results:
            key = item['name'].lower()
            if key not in seen:
                seen.add(key)
                unique_results.append(item)

        return unique_results[:20]  # Limit to top 20

    def extract_company_info(self, html: str, url: str) -> Dict[str, any]:
        """
        Extract company information from website

        Args:
            html: HTML content
            url: Website URL

        Returns:
            Dict with company details
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Extract company name
        company_name = self._extract_company_name(soup, url)

        # Extract description
        description = self._extract_description(soup)

        # Extract industry/keywords
        keywords = self._extract_keywords(soup)

        # Extract social media links
        social = self._extract_social_links(soup)

        return {
            'company': company_name,
            'description': description,
            'keywords': keywords,
            'social': social,
            'website': url
        }

    def extract_all_contacts(self, html: str, url: str) -> Dict[str, any]:
        """
        Extract all contact information from a webpage

        Args:
            html: HTML content
            url: Page URL

        Returns:
            Complete contact data dict
        """
        text = BeautifulSoup(html, 'html.parser').get_text()

        emails = self.extract_emails(text)
        phones = self.extract_phones(text)
        linkedin_profiles = self.extract_linkedin_profiles(text)
        names_with_roles = self.extract_names_with_roles(html)
        company_info = self.extract_company_info(html, url)

        return {
            'emails': list(emails),
            'phones': list(phones),
            'linkedin_profiles': list(linkedin_profiles),
            'team_members': names_with_roles,
            'company_info': company_info,
            'source_url': url,
            'total_contacts': len(emails) + len(phones) + len(names_with_roles)
        }

    def _clean_phone(self, phone: str) -> str:
        """Clean phone number formatting"""
        return re.sub(r'[^\d+]', '', phone)

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        words = text.split()

        # 2-4 words, each capitalized, no special chars
        if len(words) < 2 or len(words) > 4:
            return False

        # All words should start with capital
        if not all(w[0].isupper() for w in words if w):
            return False

        # No weird characters
        if re.search(r'[^a-zA-Z\s\'-]', text):
            return False

        return True

    def _find_role_near_name(self, name_elem) -> Optional[str]:
        """Find job role near a name element"""
        # Check next sibling
        next_elem = name_elem.find_next_sibling()
        if next_elem:
            role_text = next_elem.get_text(strip=True).lower()
            for title in self.JOB_TITLES:
                if title in role_text:
                    return next_elem.get_text(strip=True)

        # Check parent container
        parent = name_elem.parent
        if parent:
            parent_text = parent.get_text(strip=True).lower()
            for title in self.JOB_TITLES:
                if title in parent_text:
                    # Extract just the title part
                    lines = parent.get_text(strip=True).split('\n')
                    for line in lines:
                        if any(t in line.lower() for t in self.JOB_TITLES):
                            return line.strip()

        return None

    def _extract_company_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract company name from page"""
        # Try title tag
        title = soup.find('title')
        if title:
            # Remove common suffixes
            name = title.get_text()
            name = re.sub(r'\s*[-|–]\s*.*$', '', name)
            if name and len(name) < 100:
                return name.strip()

        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Fallback to domain
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.replace('www.', '').split('.')[0].title()

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract company description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']

        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']

        # Try first paragraph
        p = soup.find('p')
        if p:
            text = p.get_text(strip=True)
            if len(text) > 50:
                return text[:300]

        return ""

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords/tags from page"""
        keywords = []

        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend([k.strip() for k in meta_keywords['content'].split(',')])

        # Common industry words from text
        text = soup.get_text().lower()
        industry_words = ['saas', 'software', 'technology', 'consulting', 'services',
                         'marketing', 'sales', 'ai', 'ml', 'data', 'cloud']
        keywords.extend([word for word in industry_words if word in text])

        return list(set(keywords))[:10]

    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links"""
        social = {}

        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href'].lower()

            if 'linkedin.com/company' in href:
                social['linkedin'] = link['href']
            elif 'twitter.com' in href or 'x.com' in href:
                social['twitter'] = link['href']
            elif 'facebook.com' in href:
                social['facebook'] = link['href']

        return social


# Global instance
contact_extractor = ContactExtractor()
