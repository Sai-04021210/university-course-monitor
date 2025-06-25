-- Database initialization for Course Monitor
-- Creates tables for institutions and programmes as per the plan

-- Create institutions table
CREATE TABLE institutions (
    inst_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100), -- e.g. "Universität", "FH", "Hochschule"
    status VARCHAR(50) DEFAULT 'public', -- public or private
    location VARCHAR(255), -- city or state
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create programmes table
CREATE TABLE programmes (
    prog_id SERIAL PRIMARY KEY,
    inst_id INTEGER REFERENCES institutions(inst_id),
    program_name VARCHAR(500) NOT NULL,
    degree VARCHAR(50), -- e.g. "MSc", "BA", "PhD"
    language VARCHAR(100), -- e.g. "English", "English/German"
    tuition_fee DECIMAL(10,2) DEFAULT 0, -- in EUR
    tuition_period VARCHAR(20) DEFAULT 'semester', -- semester or year
    start_date VARCHAR(50), -- e.g. "Winter 2024", "October 2024"
    source VARCHAR(50), -- HRK, DAAD, GAC
    source_url VARCHAR(500), -- link to original listing
    accreditation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create unique constraint to prevent duplicates
CREATE UNIQUE INDEX idx_programme_unique 
ON programmes (inst_id, program_name, degree) 
WHERE is_active = TRUE;

-- Create indexes for faster queries
CREATE INDEX idx_programmes_language ON programmes (language);
CREATE INDEX idx_programmes_tuition ON programmes (tuition_fee);
CREATE INDEX idx_programmes_created ON programmes (created_at);
CREATE INDEX idx_programmes_source ON programmes (source);
CREATE INDEX idx_institutions_name ON institutions (name);
CREATE INDEX idx_institutions_type ON institutions (type);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_institutions_updated_at 
    BEFORE UPDATE ON institutions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_programmes_updated_at 
    BEFORE UPDATE ON programmes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample German public institutions
INSERT INTO institutions (name, type, status, location) VALUES
('RWTH Aachen University', 'Universität', 'public', 'Aachen'),
('Technical University of Munich', 'Universität', 'public', 'Munich'),
('University of Hamburg', 'Universität', 'public', 'Hamburg'),
('Karlsruhe Institute of Technology', 'Universität', 'public', 'Karlsruhe'),
('University of Stuttgart', 'Universität', 'public', 'Stuttgart'),
('Dresden University of Technology', 'Universität', 'public', 'Dresden'),
('University of Bonn', 'Universität', 'public', 'Bonn'),
('University of Göttingen', 'Universität', 'public', 'Göttingen'),
('University of Heidelberg', 'Universität', 'public', 'Heidelberg'),
('Free University of Berlin', 'Universität', 'public', 'Berlin')
ON CONFLICT DO NOTHING;